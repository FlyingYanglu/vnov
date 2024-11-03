from vnov.story import StoryTeller, Refiner, CharacterDesigner, Director, MidJourneySimpleCharDesigner
from vnov.story.storyboard import Storyboard


class StoryPipeline:
    def __init__(self, model):
        self.storyteller = StoryTeller(model)
        self.refiner = Refiner(model)
        self.character_designer = CharacterDesigner(model)
        self.storyboard = Storyboard(model)
        self.director = Director(model)
        self.midjourney_char_designer = MidJourneySimpleCharDesigner(model)

    def refine_novel(self, novel, **kwargs):
        self.refiner.refine_novel(novel, **kwargs)

    def tell_novel(self, novel, **kwargs):
        self.storyteller.tell_novel(novel, **kwargs)

    def generate_novel(self, novel, **kwargs):
        # original novel -> script, character_dict
        self.tell_novel(novel, **kwargs)


        # original novel, script -> characters_info.json
        self.design_all_characters(novel, **kwargs)

        # script -> midjourney character prompt
        self.midjourney_char_designer.design_all_characters(novel, **kwargs)

        # script -> refined script
        self.refine_novel(novel, **kwargs)

        # refined script -> storyboard
        self.generate_storyboards(novel, **kwargs)

        # storyboard, characters_info.json -> midjourney prompts
        self.generate_imagine_prompts(novel, mode="Midjourney")
        
        # storyboard, characters_info.json -> imagine prompts
        self.generate_imagine_prompts(novel, **kwargs)

        # imagine prompts -> diffusion images

        # midjourney prompts -> midjourney images



    def design_all_characters(self, novel, **kwargs):
        characters_info = self.character_designer.design_all_characters(novel, **kwargs)
        self.character_designer.save_characters_info(novel, characters_info)
    
    def generate_storyboards(self, novel, **kwargs):
        self.storyboard.storyborading_all_refined(novel, **kwargs)

    def generate_imagine_prompts(self, novel, **kwargs):
        self.director.run(novel)


    def start(self, novel, main_character="史金", start_chapter=1, end_chapter=3):
        self.generate_novel(novel, main_character=main_character, start_chapter=start_chapter, end_chapter=end_chapter)

