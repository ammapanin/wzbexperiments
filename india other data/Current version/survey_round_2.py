import os
from pkg.create_questionnaire import run_survey
import pkg.survey_round_2.details.cognition as cognition

india_path = os.path.dirname(os.path.abspath(__file__))
survey_path = os.path.join(india_path, "pkg", "survey_round_2")
data_path = os.path.join(survey_path, "data")
comments_path = os.path.join(india_path, "comments")
csv_path = os.path.join(survey_path, "details", "definitions")

title = "India Low Carbon Project - Questionnaire Round 2"

stimuli_tabs = [(cognition.Raven, "cognition task 1"),
                (cognition.Stroop, "cognition task 2")]

qdic = {"title": title,
        "stimuli": stimuli_tabs,
        "csv_path": csv_path,
        "data_path": data_path,
        "next_function": "comments"}

#debug = "DEBUG"
debug = False

survey = run_survey(mode = debug,
                    qoptions = qdic)

