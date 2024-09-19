# # MODEL TO DB
from sqlalchemy import create_engine
from app.database.base import Base
from app.models import *  # This imports all models
from app.database.session import get_db as db  # Assuming the database session function exists
from sqlalchemy.orm import sessionmaker
from app.database.config import engine
import uuid
import csv
from sqlalchemy.orm import Session
from sqlalchemy import func
import csv
import re






# # MODELS TO DB Tables
#region
# from sqlalchemy import create_engine
# from app.database.base import Base
# from app.models import *  # This imports all models

# DATABASE_URL = "postgresql://cameronhightower:Wellpleased22!@localhost:5432/automated_tutoring_service"
# engine = create_engine(DATABASE_URL, echo=True)  # Set echo to True to log SQL queries
# Base.metadata.create_all(engine)
#endregion





def update_question_bank(session):
    # Define the regex patterns
    # remove_single_letter = re.compile(r'\$(\w+)\$')  # Updated to handle any word characters (including multiple)
    pattern1 = r"(\\\\frac\{[^{}]*\{[^{}]*\}[^{}]*\}\{[0-9]+\})"  #works on expanding radicals specifically

    # Query to find all questions with sub_topic in the specified list
    # questions = session.query(QuestionBankQuestion).filter(QuestionBankQuestion.sub_topic.in_(['expanding_radicals'])).filter(QuestionBankQuestion.question_number_in_subtopic == 1).all()
    questions = session.query(QuestionBankQuestion).filter(QuestionBankQuestion.sub_topic.in_(['expanding_radicals'])).all()
    # questions = session.query(QuestionBankQuestion).filter(QuestionBankQuestion.sub_topic.in_(['expanding_radicals'])).all()

    for question in questions:
        # Get the current question content
        updated_content = question.question_content
        
        # Apply the regex patterns in sequence
        # updated_content = remove_single_letter.sub(r'\1', updated_content)  # Remove dollar signs around single letters
        result = re.sub(pattern1, r"\\\\(\1\\\\)", updated_content)


        question.question_content = result

    # Commit the changes to the database
    session.commit()


# Session = sessionmaker(bind=engine)
# session = Session()
# update_question_bank(session)
# session.close()



# UGH - repopoualte question_content
#region
# import pandas as pd
# # Load the CSV file
# file_path = 'backup_question_bank.csv'  # Update with the actual path
# df = pd.read_csv(file_path)


# Session = sessionmaker(bind=engine)
# session = Session()

# # Iterate over each row in the DataFrame and update the database
# for index, row in df.iterrows():
#     # Fetch the record by id
#     question = session.query(QuestionBankQuestion).filter(QuestionBankQuestion.id == row['id']).first()
    
#     if question:
#         # Update the question_content field
#         question.question_content = row['question_content']
#         session.add(question)

# # Commit the changes to the database
# session.commit()

# # Close the session
# session.close()
#endregion


def escape_equation_and_question_content():
    def escape_string(input_str):
        if input_str:
            return input_str.replace("\\", "\\\\")  # Double escape backslashes
        return input_str

    # Fetch all questions
    questions = session.query(QuestionBankQuestion).all()

    for question in questions:
        # Escape the 'equation' column
        if question.equation:
            question.equation = escape_string(question.equation)
        
        # Escape the 'question_content' column
        if question.question_content:
            question.question_content = escape_string(question.question_content)
        
        # Add the updated question to the session
        session.add(question)

    # Commit all the changes to the database
    session.commit()
    print("Backslashes in 'equation' and 'question_content' columns have been escaped.")



# Function to back up the PracticeTestQuestion table to a CSV file
def backup_practice_test_to_csv(session, output_file: str):
    # Query all records in the practice_tests_table
    practice_tests = session.query(PracticeTestQuestion).all()

    # Open a CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header (column names)
        writer.writerow([
            'id', 'practice_test', 'type', 'domain', 'skill', 'topic', 'sub_topic',
            'question_number', 'difficulty', 'figure_description', 'image', 'equation', 
            'svg', 'tabular_data', 'question_content', 'answer_explanation', 'correct_answer', 'choices'
        ])

        # Write each record as a row in the CSV file
        for practice_test in practice_tests:
            writer.writerow([
                practice_test.id,
                practice_test.practice_test,
                practice_test.type,
                practice_test.domain,
                practice_test.skill,
                practice_test.topic,
                practice_test.sub_topic,
                practice_test.question_number,
                practice_test.difficulty,
                practice_test.figure_description,
                practice_test.image,
                practice_test.equation,
                practice_test.svg,
                practice_test.tabular_data,
                practice_test.question_content,
                practice_test.answer_explanation,
                practice_test.correct_answer,
                practice_test.choices
            ])


def fix_empty_choices(session):
    # Filter the questions directly in the query
    questions = session.query(QuestionBankQuestion).filter(
        QuestionBankQuestion.choices == {
            "A": "",
            "B": "",
            "C": "",
            "D": ""
        }
    ).all()

    for question in questions:
        # Update the choices to an empty dictionary (valid JSON object)
        question.choices = {}  # This ensures it's a valid JSON object
    
    session.commit()

def swap_equation_and_image(db_session):
    # Query all records in the table
    questions = db_session.query(QuestionBankQuestion).all()

    for question in questions:
        # Swap the values of 'equation' and 'image'
        question.equation, question.image = question.image, question.equation

    # Commit the changes to the database
    session.commit()

# POPULATE QUESTION TYPES
# types = [
#     "abs_value_algebra",
#     "advanced_quantitative_reasoning",
#     "algebra_w_exponents",
#     "algebraic_inequalities",
#     "arcs_and_central_angles",
#     "area_volume",
#     "basic_word_problems",
#     "boundaries",
#     "box_foil",
#     "central_ideas_and_details_questions",
#     "circle_equations",
#     "combine_like_terms",
#     "command_of_textual_evidence_questions",
#     "completing_the_square",
#     "cqe_bar_graph_questions",
#     "cqe_table_questions",
#     "cross_text_connections_questions",
#     "data_inference",
#     "degree_radian_conversions",
#     "desmos_practice",
#     "dimensional_analysis",
#     "discriminant",
#     "distance_formula",
#     "eq_from_two_points_f_n",
#     "evaluation",
#     "expanding_radicals",
#     "exponent_properties",
#     "exponential_equations",
#     "factoring",
#     "finding_sides",
#     "form_structure_sense_questions",
#     "fractions",
#     "frequency_tables",
#     "function_notation",
#     "geometry_trig_challenge",
#     "high_degree_polynomials",
#     "identification",
#     "imaginary_numbers",
#     "inference_questions",
#     "intercepts",
#     "interpretation",
#     "midpoint",
#     "missing_average",
#     "mmmr",
#     "moc_from_figure",
#     "multi_step",
#     "one_step",
#     "parallel_and_perpendicular_slopes",
#     "percent_increase_decrease",
#     "percents",
#     "poly_long_div",
#     "probability_from_a_table",
#     "proportional_expressions",
#     "proportional_reasoning",
#     "pythag",
#     "quadratic_formula",
#     "rational_roots_th",
#     "remainder_theorem",
#     "rhetorical_synthesis_questions",
#     "similar_triangles",
#     "solutions_and_intersection",
#     "special_triangles",
#     "standard_deviation",
#     "systems_word_problems",
#     "terminology",
#     "text_structure_and_purpose_questions",
#     "transitions_questions",
#     "transversals",
#     "triangle_congruence",
#     "triangle_sum_theorem",
#     "vertex_from_different_forms",
#     "vietas",
#     "word_problems",
#     "words_in_context_questions"
# ]

def populate_question_types(db_session):
    for question_type_name in types:
        # Check if the question type already exists
        existing_question_type = db_session.query(QuestionType).filter_by(question_type_name=question_type_name).first()
        
        if not existing_question_type:
            # If it doesn't exist, create a new record
            new_question_type = QuestionType(question_type_name=question_type_name)
            db_session.add(new_question_type)
    
    # Commit the changes to the database
    db_session.commit()

# POPULATE USER QUESTION PROGRESS. ALSO YOU CAN JUST CLICK INTO THE DB ON PGADMIN4 FOR STUFF LIKE BELOW
#region

this_uuid = uuid.UUID("550e8400-e29b-41d4-a716-446655440000")
this_id = 64
progress = 1
def populate_user_question_progress(db_session):
 
    new_progress = UserQuestionProgress(user_id = this_uuid, question_type_id=64)
    db_session.add(new_progress)
    
    # Commit the changes to the database
    db_session.commit()

#endregion



# Function to back up the QuestionBankQuestion table to a CSV file
def backup_question_bank_to_csv(session, output_file: str):
    # Query all records in the table
    questions = session.query(QuestionBankQuestion).all()

    # Open a CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header (column names)
        writer.writerow([
            'id', 'topic', 'sub_topic', 'question_number_in_subtopic', 'figure_description',
            'image', 'equation', 'svg', 'question_content', 'answer_explanation',
            'correct_answer', 'tabular_data', 'choices'
        ])

        # Write each record as a row in the CSV file
        for question in questions:
            writer.writerow([
                question.id,
                question.topic,
                question.sub_topic,
                question.question_number_in_subtopic,
                question.figure_description,
                question.image,
                question.equation,
                question.svg,
                question.question_content,
                question.answer_explanation,
                question.correct_answer,
                question.tabular_data,
                question.choices
            ])
Session = sessionmaker(bind=engine)
session = Session()
backup_practice_test_to_csv(session, "qb_backup.csv")
session.close()







def update_question_bank_archive(session):
    # Define the regex patterns
    # remove_single_letter = re.compile(r'\$(\w+)\$')  # Updated to handle any word characters (including multiple)
    # remove_numbers = re.compile(r'\$(\d+(\.\d+)?)\$')  # Updated to handle decimals
    # remove_percentage = re.compile(r'\$(\d+%)\$')  # Regex to remove dollar signs around percentages
    # remove_double_backslashes = re.compile(r'\\\\')  # Regex to remove any double backslashes
    # remove_percentage_with_signs = re.compile(r'\$(\d+%)\$')  # Regex to remove dollar signs around percentages
    # remove_backslashes_before_percent = re.compile(r'\\%')  # Regex to remove backslashes before percentage signs
    # remove_dollar_signs = re.compile(r'\$')
    # replace_dollar_signs = re.compile(r'\$')

    # Query to find all questions with sub_topic in the specified list
    # questions = session.query(QuestionBankQuestion).filter(QuestionBankQuestion.sub_topic.in_(['advanced_quantitative_reasoning'])).filter(QuestionBankQuestion.question_number_in_subtopic == 43).all()
    questions = session.query(QuestionBankQuestion).filter(~QuestionBankQuestion.sub_topic.in_(['frequency_tables'])).all()

    for question in questions:
        # Get the current question content
        updated_content = question.question_content
        
        # Apply the regex patterns in sequence
        # updated_content = remove_single_letter.sub(r'\1', updated_content)  # Remove dollar signs around single letters
        # updated_content = remove_numbers.sub(r'\1', updated_content)  # Remove dollar signs around numbers (including decimals)
        # updated_content = remove_percentage.sub(r'\1', updated_content)  # Remove dollar signs around percentages
        # updated_content = remove_double_backslashes.sub(r'', updated_content)  # Remove double backslashes
        # updated_content = remove_backslashes_before_percent.sub('%', updated_content)  # Remove backslashes before percentage signs
        # updated_content = remove_percentage_with_signs.sub(r'\1', updated_content)  # Remove dollar signs around percentages
        # updated_content = remove_dollar_signs.sub(r'', updated_content)
        # updated_content = remove_double_backslashes_before_percent.sub('%', updated_content)
        # if updated_content:  # Check if the dictionary is not empty
        #     updated_content = {
        #         key: replace_dollar_signs.sub(lambda match, c=[0]: '\\(' if c.append(c.pop() + 1) or c[0] % 2 == 1 else '\\)', value, 2)
        #         for key, value in updated_content.items()
        #     }      
        # Update the question_content with the modified text
        question.question_content = updated_content

    # Commit the changes to the database
    session.commit()