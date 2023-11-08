# Utilities 
import random
import time
import json

# Logging libraries
import logging
import argparse

try:
    # Browser interaction
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By

    # Machine learning
    from huggingface_hub.inference_api import InferenceApi
    import os
except ModuleNotFoundError:
	if "y" in input("Install dependencies? [y/N] > ").lower():
		os.system("python3 -m pip install -r requirements.txt")

# Configuration file
def read_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)
    return config


# Argparse configuration
parser = argparse.ArgumentParser(description="Kahoot Bot")
parser.add_argument("--debug", action="store_true", help="Enable debug mode")
parser.add_argument("--nickname", type=str, help="Your Kahoot nickname")
parser.add_argument("--gamepin", type=int, help="Your Kahoot game-pin")
args = parser.parse_args()

# Logger configuration
log_level = logging.DEBUG if args.debug else logging.INFO
logging.basicConfig(filename="kahoot_bot.log", level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")
logger = logging.getLogger("kahoot_bot_logger")

class KahootBot:
    """
    A Kahoot bot that can join games and answer questions autonomously
    """
    config = read_config("configuration.json")

    MODEL_API_TOKEN = config["MODEL_API_TOKEN"]
    KAHOOT_URL = "https://kahoot.it"
    KAHOOT_JOIN_URL = f"{KAHOOT_URL}/"
    NICKNAME_PAGE_URL = f"{KAHOOT_URL}/join"
    GAME_BLOCK_URL = f"{KAHOOT_URL}/gameblock"
    RANKING_URL = "https://kahoot.it/v2/ranking/"

    def __init__(self, nickname: str = None, is_headless: bool = False):
        """
        Initializes the Kahoot bot.
        Args:
            nickname: str
                Kahoot nickname
            is_headless: bool
                Whether to run bot in headless mode
        """
        self.driver = self.init_driver(is_headless)
        #self.model = self.init_model()

        if nickname == None:
            self.nickname = self.__class__.config["NICKNAME"]
        self.nickname = nickname

        logger.info("KahootBot: initialized")
    
    def init_driver(self, is_headless: bool):
        """
        Helper function for initializing Chrome WebDriver object to interact with Kahoot.it
        Args:
            is_headless: bool
                Whether to run bot in headless mode
        Returns:
            WebDriver: selenium.webdriver.Chrome
                The initialized WebDriver.
        """
        try:
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            if is_headless:
                chrome_options.add_argument("--headless")
            return webdriver.Chrome(options=chrome_options)
        except Exception as e:
            raise Exception(f"ChromeDriver: initialization error - {e}")

    def init_model(self):
        """
        Helper function for initializing HuggingFace API object to interact with GPT2 model
        Args:
            is_headless: bool
                Whether to run bot in headless mode
        Returns:
            model: huggingface_hub.inference_api.InferenceAPI
                The initialized HuggingFace API object
        """
        self.model_params = {"max_length": 256, "penalty_alpha": 0.6, "top_k": 4}
        try:
            return InferenceApi(
                repo_id="gpt2-large", token=self.__class__.MODEL_API_TOKEN
            )
        except Exception as e:
            raise Exception(f"Model: initialization error - {e}")

    def validate_answer(self, question: str, answer: str) -> bool:
        """
        Helper function for checking if an answer is correct for a given question
        Args:
            question: str
                The given question
            answer: str
                The given question
        Returns:
            is_correct: bool
                Whether the answer is correct.
        """
        try:
            prompt = f"{question} {answer}. Is that correct? Say yes or no. "
            result = self.model(prompt, self.model_params)
            generated_text = result[0]["generated_text"].lower()
            if "yes" in generated_text:
                return True
            return False
        except Exception as e:
            raise Exception(f"Answer validation error: {e}")
    
    def is_visible(self, name = None, css_selector = None) -> bool:
        """
        Helper function for checking if an element is visible
        Args:
            name: str
                The element name
            css_selector: str
                The css selector for the element
        Returns:
            is_visible: bool
                Whether the requested element is visible.
        """
        if css_selector == None:
            return len(self.driver.find_elements(By.NAME, name)) > 0
        elif name == None:
            return len(self.driver.find_elements(By.CSS_SELECTOR, css_selector)) > 0
        else:
            raise Exception("Argument: Missing name or css selector")
        
    def wait_until_url(self, target_url: str):
        """
        Helper function for waiting until the Chrome WebDriver navigates to a target url
        Args:
            target_url: str
                The target url
        """
        while self.driver.current_url != target_url:
            pass


    def join_game(self, game_pin: str):
        """
        Joins a Kahoot game with a given game pin
        Args:
            game_pin: str
                The Kahoot game pin
        """

        # Navigate to join page
        self.driver.get(self.__class__.KAHOOT_JOIN_URL)
        self.wait_until_url(self.__class__.KAHOOT_JOIN_URL)
        logger.info("Navigation: complete")

        # Check for available game pin field
        is_pin_field_found = self.is_visible(name = "gameId")
        if not is_pin_field_found:
            raise Exception("Game pin field not found")
        logger.info("Game pin field: found")

        # Fill in game pin field
        pin_field = self.driver.find_element(By.NAME, "gameId")
        pin_field.clear()
        pin_field.send_keys(game_pin)
        pin_field.send_keys(Keys.RETURN)
        logger.info("Game pin field: submitted")

        # Check game pin validity by checking for errors
        time.sleep(1)
        if(self.is_visible(css_selector = ".dnIsMS")):
            raise Exception("Game pin: invalid")

        # Check for available nickname field
        self.wait_until_url(self.__class__.NICKNAME_PAGE_URL)
        is_nickname_field_found = self.is_visible(name = "nickname")
        while not is_nickname_field_found:
            is_nickname_field_found = self.is_visible(name = "nickname")
            pass
        logger.info("Nickname field: found")

        # Fill in nickname
        nickname_field = self.driver.find_element(By.NAME, "nickname")
        nickname_field.clear()
        nickname_field.send_keys(self.nickname)
        nickname_field.send_keys(Keys.RETURN)
        logger.info("Nickname field: filled")

        # Check nickaname validity by checking if there is an error
        time.sleep(1)
        if(self.is_visible(css_selector = '[role="alert"]')):
            raise Exception("Nickname: invalid")

    def is_question_shown(self):
        return self.is_visible(css_selector = '[data-functional-selector="block-title"]') 
    
    def is_multiselect(self):
        return self.is_visible(css_selector = '[data-functional-selector^="submit"]')
    

    def find_viable_answer_elements(self):
        viable_answer_elements = self.driver.find_elements(
            By.CSS_SELECTOR, '[data-functional-selector^="answer"]'
        )
        if len(viable_answer_elements) == 0:
            return -1
        return viable_answer_elements

    def pick_answer(self, question, viable_answer_elements: list):
        """
        Retrieves correct answers for a well-defined and provided question
        """
        return random.choice(viable_answer_elements)
        viable_answers = [
            viable_answer_element.text
            for viable_answer_element in viable_answer_elements
        ]
        for i, viable_answer in enumerate(viable_answers):
            if self.validate_answer(question, viable_answer):
                return viable_answer_elements[i]
        logger.info("Answer search returned nothing")
        return random.choice(viable_answer_elements)
    
    def is_game_over(self):
        return self.driver.current_url == self.__class__.RANKING_URL
    
    def play_game(self, game_pin: str):
        """
        Plays game automatically
        """
        # Join game
        self.join_game(game_pin)
        logger.info(f"Game {game_pin}: joined")

        # Standard game loop
        question_num = 0
        while True:
            if self.is_game_over():
                # Display rankings
                time.sleep(5)
                logger.info(f"Game {game_pin}: finished")

                # Quit game loop
                self.driver.quit()
                break

            # Await question block
            self.wait_until_url(self.__class__.GAME_BLOCK_URL)
            logger.info("Question block: started")

            # Identify question characteristics
            logger.info(f"Question displayed: {self.is_question_shown()}")
            logger.info(f"Multi-select question: {self.is_multiselect()}")

            # Identify viable answers
            viable_answer_elements = self.find_viable_answer_elements()
            if viable_answer_elements == -1:
                pass
            logger.info("Viable answers: found")

            # Pick question choice
            if self.is_question_shown():
                question_element = self.driver.find_element(By.CSS_SELECTOR, '[data-functional-selector="block-title"]')
                question = question_element.text
                answer_choice = self.pick_answer(
                    question, viable_answer_elements
                )

            else:
                answer_choice = random.choice(viable_answer_elements)

            logger.info("Answer: chosen")

            # Click answer
            answer_choice.click()
            logger.info(f"Answer: {question_num} submitted")
            question_num += 1

try:
    nickname = None
    if args.nickname:
        nickname = args.nickname
    myBot = KahootBot(nickname, False)
except Exception as e:
    logger.error(f"Bot initialization failed: {e}")

try: 
    if args.gamepin:
        user_game_pin = args.gamepin
    else:
        user_game_pin = input("Kahoot game pin: ").strip().lower()
    myBot.play_game(user_game_pin)
except Exception as e:
    logger.error(f"Game play failed: {e}")
    myBot.driver.quit()


    
