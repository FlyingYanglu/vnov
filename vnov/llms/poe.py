from vnov.llms.base import BaseLLM
import time
from poept import PoePT
from vnov.configs import CONFIG
import random
from poept.exceptions import ToomanyRequestsException, TimeoutException

class Poe(BaseLLM):
    def __init__(self, email_account=CONFIG["Poe"]["email"], **kwargs):
        self.bot = PoePT()
        self.construct_email_dict(email_account)
        self.current_email = None
        self.switch_email()
        self.bot.login(self.current_email)

        self.bot_id = kwargs.get("bot_id", None)
        self.max_length = kwargs.get("max_length", 3800)
        self.gen_interval = kwargs.get("gen_interval", 20)

    

    def construct_email_dict(self, email_account):
        print("Constructing email dict out of email accounts", email_account)
        self.email_dict = {"available": [], "unavailable": []}
        for email_account in email_account:
            self.email_dict["available"].append(email_account)

    def token_length(self, context):
        return self.max_length - len(context)

    def switch_email(self, rate_limit=False):
        print("Switching email")
        if self.bot is not None:
            self.bot.close()
            self.bot = PoePT()
        if self.current_email is not None:
            
            if not rate_limit:
                self.email_dict["unavailable"].append(self.current_email)
                
            else:
                self.email_dict["available"].append(self.current_email)

        if len(self.email_dict["available"]) == 0:
            raise Exception("No available email account")
        
        if rate_limit and len(self.email_dict["available"]) == 1:
            print("Rate limit exceeded and only one email account available, waiting for 15 minutes")
            time.sleep(60*15)
        # pop the first available email
        self.current_email = self.email_dict["available"].pop(0)
        self.bot.login(self.current_email)
        print("Switched to new email account", self.current_email)

    def generate(self, context, **kwargs):
        if isinstance(context, str):
            context = context
        elif isinstance(context, dict):
            context = context[-1]["content"]
        new_chat = kwargs.get("new_chat", False)
        bot_id = kwargs.get("bot_id", self.bot_id)
        if not bot_id:
            raise ValueError("bot_id must be provided")
        try:
            response = self.bot.ask(newchat=new_chat, bot=bot_id, prompt=context)
            time.sleep(random.randint(int(self.gen_interval*(3/4)), int(self.gen_interval*(5/4))))
            return response
        except Exception as e:
            if type(e) == TimeoutException:
                print("Timeout, waiting for 10 seconds and switch to new email")
                time.sleep(10)
                print("Switching email due to timeout, might be no credits")
                self.switch_email()
            elif type(e) == ToomanyRequestsException:
                print("Rate limit exceeded, attempting to switch email")
                time.sleep(10)
                print("Switching email due to rate limit")
                self.switch_email(rate_limit=True)

            raise e
    

    def __call__(self, context, **kwargs):
        return self.generate(context, **kwargs)
    
    def __del__(self):
        # TODO: after finish testing, uncomment
        # self.bot.close()
        pass

