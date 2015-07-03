import os
from pkg.create_questionnaire import run_survey


india_path = os.path.dirname(os.path.abspath(__file__))
survey_path = os.path.join(india_path, "pkg", "lcf survey", "details")
data_path = os.path.join(survey_path, "data")
comments_path = os.path.join(survey_path, "comments")
csv_path = os.path.join(survey_path,
                        "definitions")

title = "India Low Carbon Project - LCF Formats"

stimuli_tabs = None

qdic = {"title": title,
        "stimuli": stimuli_tabs,
        "csv_path": csv_path,
        "data_path": data_path,
        "next_function": "comments"}

debug = "DEBUG"

survey = run_survey(mode = debug,
                    qoptions = qdic)

