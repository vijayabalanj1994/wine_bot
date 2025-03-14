from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet

import openai
import os
import json

client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GetWineRecommendation(Action):
    """Processes user inout to classify wine preferences (food, occasion, taste) using GPT-4"""
    def name(self) -> Text:
        return "action_get_wine_recommendation"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        food = tracker.get_slot("food_pairing")
        occasion = tracker.get_slot("occasion")
        taste = tracker.get_slot("taste_preference")

        prompt = f"""
                I am a sommelier bot. Based on the following preferences, recommend the best wine:
                - Food Pairing: {food}
                - Occasion: {occasion}
                - Taste Preference: {taste}

                Provide a response in JSON format:
                {{
                  "wine_name": "The name of the wine recommended. Example: Château Margaux 2015",
                  "wine_description": " A short description of the recommended wine, including its taste profile and why it pairs well. Example: A full-bodied red wine with rich dark fruit flavors, perfectly paired with steak.",
                  "wine_price": "Estimated price in GBP. Example: 25.99"
                }}
                
                """

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )

            gpt_response = response.choices[0].message.content
            wine_data = json.loads(gpt_response)

            # dispatcher.utter_message(
            #     text=f"I recommend **{wine_data['wine_name']}**! 🍷 {wine_data['wine_description']} \n💲 Price: **${wine_data['wine_price']}**."
            # )

            return [
                SlotSet("wine_name", wine_data["wine_name"]),
                SlotSet("wine_description", wine_data["wine_description"]),
                SlotSet("wine_price", wine_data["wine_price"])
            ]

        except Exception as e:
            # dispatcher.utter_message(
            #     text="Hmm, I couldn't find the perfect match. Would you like to try a popular red wine instead?")
            return [SlotSet("wine_name", None)]


# class ActionCheckSufficientFunds(Action):
#     def name(self) -> Text:
#         return "action_check_sufficient_funds"
#
#     def run(
#         self,
#         dispatcher: CollectingDispatcher,
#         tracker: Tracker,
#         domain: Dict[Text, Any],
#     ) -> List[Dict[Text, Any]]:
#         # hard-coded balance for tutorial purposes. in production this
#         # would be retrieved from a database or an API
#         balance = 1000
#         transfer_amount = tracker.get_slot("amount")
#         has_sufficient_funds = transfer_amount <= balance
#         return [SlotSet("has_sufficient_funds", has_sufficient_funds)]
