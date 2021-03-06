import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse

from polls.models import Question


def create_question(question_text, days):
    """
    Creates a question with the given `question_text` published the given
    number of `days` offset to now (negative for questions published
    in the past, positive for questions that have yet to be published).
    """
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexDetailTest(TestCase):

    def test_detail_view_with_future_question(self):
        future_question = create_question("Future question", 30)
        response = self.client.get(reverse("polls:detail",
                                           args=(future_question.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_past_question(self):
        past_question = create_question("Past question", -12)
        response = self.client.get(reverse("polls:detail",
                                           args=(past_question.id,)))
        self.assertContains(response, past_question.question_text,
                            status_code=200)


class QuestionViewTests(TestCase):

    def test_index_view_with_no_questions(self):
        """If no questions exsit, an appropriate message should be displayed."""
        response = self.client.get(reverse("polls:index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available")
        self.assertQuerysetEqual(response.context["latest_questions"], [])

    def test_index_view_with_a_past_question(self):
        """Questions with a pub_date in the past should be displayed on the
        index page
        """
        create_question(question_text="Past question", days=-30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(
            response.context["latest_questions"], ["<Question: Past question>"]
        )

    def test_index_view_with_a_future_question(self):
        create_question("Future question", 30)
        response = self.client.get(reverse("polls:index"))
        self.assertContains(response, "No polls are available", status_code=200)
        self.assertQuerysetEqual(response.context["latest_questions"], [])

    def test_index_view_with_future_and_past_question(self):
        create_question("Future question", 30)
        create_question("Past question", -30)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_questions"],
                                 ["<Question: Past question>"])

    def test_index_view_with_two_past_question(self):
        create_question("Past question 1", -30)
        create_question("Past question 2", -12)
        response = self.client.get(reverse("polls:index"))
        self.assertQuerysetEqual(response.context["latest_questions"],
                                 ["<Question: Past question 2>",
                                  "<Question: Past question 1>"])



class QuestionMethodTest(TestCase):

    def test_was_published_recently_with_future_question(self):
        """was_published_recently() should return False for question with a
        pub_date in the future."""
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertEqual(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        time = timezone.now() - datetime.timedelta(days=1)
        old_question = Question(pub_date=time)
        self.assertEqual(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        time = timezone.now() - datetime.timedelta(minutes=1)
        recent_question = Question(pub_date=time)
        self.assertEqual(recent_question.was_published_recently(), True)
