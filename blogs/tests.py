from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import BlogPost


class BlogPostModelTests(TestCase):
    def test_post_displays_title_and_belongs_to_author(self):
        author = get_user_model().objects.create_user('author', password='test-password')

        post = BlogPost.objects.create(owner=author, title='Первая публикация', text='Текст публикации')

        self.assertEqual(str(post), 'Первая публикация')
        self.assertEqual(post.owner, author)
        self.assertIsNotNone(post.date_added)


class BlogAccessTests(TestCase):
    def setUp(self):
        self.author = get_user_model().objects.create_user('author', password='test-password')
        self.other_user = get_user_model().objects.create_user('other', password='test-password')
        self.own_post = BlogPost.objects.create(owner=self.author, title='Запись автора', text='Текст автора')
        self.other_post = BlogPost.objects.create(owner=self.other_user, title='Чужая запись', text='Чужой текст')

    def test_home_is_public_and_orders_new_posts_first(self):
        newer_post = BlogPost.objects.create(owner=self.author, title='Новая запись', text='Новее')

        response = self.client.get(reverse('blogs:home'))

        content = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertLess(content.index(newer_post.title), content.index(self.own_post.title))
        self.assertContains(response, self.other_post.title)

    def test_empty_blog_has_clear_message(self):
        BlogPost.objects.all().delete()

        response = self.client.get(reverse('blogs:home'))

        self.assertContains(response, 'Публикаций пока нет')

    def test_new_post_requires_login(self):
        response = self.client.get(reverse('blogs:post_new'))

        self.assertRedirects(response, f"{reverse('users:login')}?next={reverse('blogs:post_new')}")

    def test_new_post_assigns_current_user_even_if_owner_is_forged(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('blogs:post_new'),
            {'title': 'Новая публикация', 'text': 'Содержимое', 'owner': self.other_user.pk},
        )

        post = BlogPost.objects.get(title='Новая публикация')
        self.assertRedirects(response, reverse('blogs:home'))
        self.assertEqual(post.owner, self.author)

    def test_author_can_edit_own_post(self):
        self.client.force_login(self.author)

        response = self.client.post(
            reverse('blogs:post_edit', args=[self.own_post.pk]),
            {'title': 'Исправленная запись', 'text': 'Исправленный текст'},
        )

        self.own_post.refresh_from_db()
        self.assertRedirects(response, reverse('blogs:home'))
        self.assertEqual(self.own_post.title, 'Исправленная запись')

    def test_foreign_and_missing_edits_return_404(self):
        self.client.force_login(self.author)

        foreign_response = self.client.get(reverse('blogs:post_edit', args=[self.other_post.pk]))
        missing_response = self.client.get(reverse('blogs:post_edit', args=[9999]))

        self.assertEqual(foreign_response.status_code, 404)
        self.assertEqual(missing_response.status_code, 404)
