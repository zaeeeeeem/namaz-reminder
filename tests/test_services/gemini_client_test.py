import unittest
from unittest.mock import patch, MagicMock

import app.services.gemini_client as gemini_client


class TestGeminiClient(unittest.TestCase):

    @patch("app.services.gemini_client.load_dotenv")
    @patch.dict("os.environ", {}, clear=True)
    def test_initialize_model_missing_api_key(self, mock_load_dotenv):
        model = gemini_client._initialize_ai_model()
        self.assertIsNone(model)

    @patch("app.services.gemini_client.genai.GenerativeModel")
    @patch("app.services.gemini_client.genai.configure")
    @patch.dict("os.environ", {"GEMINI_API_KEY": "dummy_api_key"})
    def test_initialize_model_success(self, mock_configure, mock_model_class):
        mock_model_instance = MagicMock()
        mock_model_class.return_value = mock_model_instance

        model = gemini_client._initialize_ai_model()
        self.assertEqual(model, mock_model_instance)
        mock_configure.assert_called_once_with(api_key="dummy_api_key")
        mock_model_class.assert_called_once()

    @patch("app.services.gemini_client.model", None)
    def test_get_ai_response_when_model_not_initialized(self):
        response = gemini_client.get_ai_response("What is Fajr?")
        self.assertIn("not configured", response)

    @patch("app.services.gemini_client.model")
    def test_get_ai_response_success(self, mock_model):
        mock_response = MagicMock()
        mock_response.text = "Fajr is the first prayer of the day."
        mock_model.generate_content.return_value = mock_response

        user_input = "What is Fajr prayer?"
        response = gemini_client.get_ai_response(user_input)

        self.assertEqual(response, "Fajr is the first prayer of the day.")
        mock_model.generate_content.assert_called_once_with(user_input)

    @patch("app.services.gemini_client.model")
    def test_get_ai_response_exception_handling(self, mock_model):
        mock_model.generate_content.side_effect = Exception("API failure")

        response = gemini_client.get_ai_response("Tell me about Wudu.")
        self.assertIn("unable to respond", response)
