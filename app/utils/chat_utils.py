from openai import OpenAI

client = OpenAI(api_key='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')
from openai import OpenAI

from duckduckgo_search import DDGS
import re
from sqlalchemy.orm import Session
from app.models import UserQuestionProgress, QuestionType, QuestionBankQuestion, PracticeTestQuestion
from app.schemas import GetQBQuestionResponse
from sqlalchemy.dialects.postgresql import UUID
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, APIRouter, Form
from app.database.session import get_db  # Assuming the database session function exists
from app.utils.db_rtrvl_utils import get_user_progress_on_question_type, get_question_by_sub_topic_and_number, increment_user_progress
from typing import Optional, Dict, List
from pydantic import BaseModel
from typing import List



client = OpenAI()

potential_topic_confusion = """
  If the student is practicing command of quantitative evidence from a graph or table while in a reading/writing session, specify this in the action parameter so that a math question is not pulled.
"""

prompt = f"""
You are an expert SAT tutor who is leading a tutoring session.
Sessions are centered around working on questions together.  Pull questions from the question bank or practice test bank using your actions by default.  Avoid coming up with your own questions.
You operate in a loop of 4 phases: Thought, Action, PAUSE, and Observation.
At the end of the loop you will output an Answer.
1. Thought: Use Thought to describe which action, if any, to take
2. Action: If applicable, execute the chosen action using the format Action: <action_name>: <parameters>. Use one of the available actions below.
Then return “PAUSE.”
3. Observation: If an action was present, after "PAUSE", you will receive the result of your action in the form of an "Observation".
4. Answer: If an action was taken, you will use the Observation to provide your final response.  Otherwise, your answer will be an explanation or continuation of the conversation.

Your available actions are:
  
1. retrieve_qb_question: 
Retrieve a question from a question bank (e.g., Action: retrieve_qb_question: We need a question on interpreting linear equations)
2. retrieve_pt_question:
Retrieve a question from a practice test (e.g., Action: retrieve_pt_question: [specify question based on some logic])
3. web_search: 
Search the web for the answer to a question about SAT dates, deadlines, and updates or any other question that you don't have the answer to (e.g., Action: web_search: When is the next SAT?)

If there are no actions to take your Answer will be explaining a concept to the student or continuing the conversation. e.g. Answer: (explanation or continuation)

Example query:

Conversation State: The student is practicing command of quantitative evidence from a graph while in a reading/writing session.
Thought: I should pull a question from the reading and writing section testing command of quantitative evidence from a graph using retrieve_qb_question
Action: retrieve_qb_question: We need a question from the reading and writing topic that tests command of quantiative evidence from a graph.
PAUSE

You will then receive the result of your action.

Observation: [Question Metadata]

(The question has been displayed to user so you do not need to come up with a question) 

You then output:

Answer: Try this question -- let me know if you get stuck.

The loop will end here now that you have provided an answer.

Note: {potential_topic_confusion}

""".strip()

class Agent:
    def __init__(self, system = prompt):
        self.messages = []

        if isinstance(system, list):
            # Initialize with a list of dictionaries
            self.messages = system
        elif isinstance(system, str) and system:
            # Initialize with a system message string
            self.messages.append({
                "role": "system", 
                "content": system,  #
                "type": "text"      
            })

    def __call__(self, message):
        if isinstance(message, list):
            # Assuming the list contains dictionaries in the expected format
            for msg in message:
                if 'role' in msg and 'content' in msg and 'type' in msg:
                    self.messages.append(msg)
                else:
                    raise ValueError("Each message must contain 'role', 'content', and 'type'.")
        else:
            # Append a single user message
            self.messages.append({
                "role": "user", 
                "content": message,  # Content is a plain string
                "type": "text"       # Assuming "type" is required
            })
        result = self.execute()
        self.messages.append({
            "role": "assistant", 
            "content": result,  # Content is a plain string
            "type": "text"      # Assuming "type" is required
        })
        return result

    def execute(self):
        completion = client.chat.completions.create(
                        model="gpt-4o-mini", 
                        temperature=0.7,
                        messages=self.messages)
        return completion.choices[0].message.content

question_descriptions = [
    """Data Analysis:
    1. Frequency Tables
    2. Center shape and spread: Standard Deviation
    3. Center shape and spread: Measures of Center, skewed versus normal
    4. Data Inference
    5. Mean, median, mode, and range""",
    
    """Quadratics:
    1. Discriminant: use the discriminant to determine the number of real roots of a quadratic equation
    2. Quadratic Formula
    3. Factoring
    4. Remainder Theorem: given a quadratic function, find the remainder when the function is divided by a linear factor OR find the linear factor when the remainder is given
    5. Vertex from factored form, standard form, vertex form: given a quadratic function in factored form, standard form, or vertex form, find the vertex of the parabola
    6. Vieta's Formula (Sum of Roots): use Vieta's formula, -b/a, to find the sum of the roots of a quadratic equation.  Product of roots is not included in this dataset.""",
    
    """Geometry:
    1. Triangle Sum Theorem: Angles in a triangle add up to 180 degrees
    2. Special Triangles: 30-60-90, 45-45-90
    3. Area and Volume
    4. Parallel lines and a transversal
    5. Pythagorean Theorem
    6. Congruence Proofs (SAS, ASA, SSS, AAS)
    7. Arcs and Central Angles
    8. Similar Triangles
    9. Equation of a Circle
    10. Distance Formula
    11. Midpoint Formula
    12. Challenge Problems: this is a special set of questions that each include multiple geometry and trigonometry concepts and are designed to challenge the student""",
    
    """Linear Equations:
    1. Linear Relationship Word Problems
    2. Interpreting Linear Equations
    3. Equation from two points: given two points, find the equation of the line
    4. Slopes of Parallel/Perpendicular Lines""",
    
    """Algebra:
    1. Solve one step equation
    2. Solve multi step equation
    3. Algebraic Inequalities
    4. Algebra with Exponents
    5. Algebra with Absolute Value
    6. Word Problem to Algebraic Statement
    7. Proportional expressions: e.g. if 3x + 4y = 12, what is 6x + 8y? (24) """,
    
    """Terminology:
    1. Terminology: Math Vocabulary such as integer, rational number, irrational number, prime number, composite number, factor, multiple, etc.""",
    
    """Arithmetic:
    1. Fractions
    2. Combining Like Terms
    3. Exponent Properties
    4. Percents
    5. Box/FOIL
    6. F(x) notation
    7. Evaluation, e.g. evaluate 3x + 4y when x = 2 and y = 3
    8. Percent Increase/Decrease""",
    
    """Advanced Arithmetic:
    1. Expanding radicals
    2. Dimensional analysis and unit conversions
    3. Imaginary numbers
    4. Polynomial Long Division
    5. Completing the Square
    6. Rational Roots Theorem
    7. Missing Number Given Averages Problem : given the average of a set of numbers and the average of a subset of those numbers, find the average of the remaining numbers or find the missing number
    8. Complex Numerical Reasoning/Challenge Problems, this is a special set of questions designed to challenge the student -- these are often found at the end of the harder second section of the SAT""",

    
    """Exponential Equations:
    1. Linear vs. Exponential
    2. Word Problem to Exponential Equation""",
    
    """Systems:
    1. Desmos: Desmos can be used when two equations are given and we need to simply find the intersection point(s) 
    2. Intersection points and solutions algebraically: this is a special kind of problem where simply plugging the equations into Desmos does not work
    3. Word Problems: usually involes converting a word problem into a system of equations""",
    
    """Trigonometry:
    1. Trig Ratios
    2. Rad/Deg Conversions""",
    
    """Proportional Reasoning:
    1. A-List Math Fundamentals Type: these only take one of two forms: 1. You are given two objects and you can set up a proportinoal relationship directly, cross multiply and solve, or you are given a total and you must understand that the ratios must be added together to set up a proportional relationship""",
    
    """Probability:
    1. From a table, 'and', 'or'""",
    
    """Nonlinear Functions:
    1. Local extrema and intercepts given a graph""",
    
    """Intercepts:
    1. From multiple equation types: find intercepts from a variety of equation types""",

    """Reading and Writing:
    1. Boundaries: related to sentence boundaries and the use of periods, semicolons, and coordinating conjunctions
    2. Central Ideas and Details: related to reading comprehension
    3. Command of Textual Evidence: related to understanding arguments and evidence in a text
    4. Command of Quantitative Evidence given a bar graph
    5. Command of Quantitative Evidence given a table
    6. Cross text Connections: invovles understanding how two texts relate to each other
    7. Form, Structure, and Sense: related to subject verb agreement and pronoun antecedent agreement
    8. Inference Questions: invovles making inferences from a text
    9. Rhetorical Synthesis: involes adding a sentence to a paragprah to bolster or support the main idea or argument
    10. Text Structure and Purpose: asks the student to identify the purpose of a sentence within a paragraph
    11. Transitions: tests knowledge of transitional words and phrases like however, nevertheless, consequently, etc...
    12. Words in Context: tests knowledge of vocabulary in context"""
]

question_mapping = {
    1: {  # Data Analysis
        1: "frequency_tables",
        2: "standard_deviation",
        3: "moc_from_figure",
        4: "data_inference",
        5: "mmmr"
    },
    2: {  # Quadratics
        1: "discriminant",
        2: "quadratic_formula",
        3: "factoring",
        4: "remainder_theorem",
        5: "vertex_from_different_forms",
        6: "vietas"
    },
    3: {  # Geometry
        1: "triangle_sum_theorem",
        2: "special_triangles",
        3: "area_volume",
        4: "transversals",
        5: "pythag",
        6: "triangle_congruence",
        7: "arcs_and_central_angles",
        8: "similar_triangles",
        9: "circle_equations",
        10: "distance_formula",
        11: "midpoint",
        12: "geometry_trig_challenge"
    },
    4: {  # Linear Equations
        1: "word_problems",
        2: "interpretation",
        3: "eq_from_two_points_f_n",
        4: "parallel_and_perpendicular_slopes"
    },
    5: {  # Algebra
        1: "one_step",
        2: "multi_step",
        3: "algebraic_inequalities",
        4: "algebra_w_exponents",
        5: "abs_value_algebra",
        6: "basic_word_problems",
        7: "proportional_expressions"
    },
    6: {  # Terminology
        1: "terminology"
    },
    7: {  # Arithmetic
        1: "fractions",
        2: "combine_like_terms",
        3: "exponent_properties",
        4: "percents",
        5: "box_foil",
        6: "function_notation",
        7: "evaluation",
        8: "percent_increase_decrease"
    },
    8: {  # Advanced Arithmetic
        1: "expanding_radicals",
        2: "dimensional_analysis",
        3: "imaginary_numbers",
        4: "poly_long_div",
        5: "completing_the_square",
        6: "rational_roots_th",
        7: "missing_average",
        8: "advanced_quantitative_reasoning"
    },
    9: {  # Exponential Equations
        1: "identification",
        2: "exponential_equations"
    },
    10: {  # Systems
        1: "desmos_practice",
        2: "solutions_and_intersection",
        3: "systems_word_problems"
    },
    11: {  # Trigonometry
        1: "finding_sides",
        2: "degree_radian_conversions"
    },
    12: {  # Proportional Reasoning
        1: "proportional_reasoning"
    },
    13: {  # Probability
        1: "probability_from_a_table"
    },
    14: {  # Nonlinear Functions
        1: "high_degree_polynomials"
    },
    15: {  # Intercepts
        1: "intercepts"

    },
    16: {  # Reading and Writing
        1: "boundaries",
        2: "central_ideas_and_details_questions",
        3: "command_of_textual_evidence_questions",
        4: "cqe_bar_graph_questions",
        5: "cqe_table_questions",
        6: "cross_text_connections_questions",
        7: "form_structure_sense_questions",
        8:  "inference_questions",
        9:  "rhetorical_synthesis_questions",
        10: "text_structure_and_purpose_questions",
        11: "transitions_questions",
        12: "words_in context_questions"
    },
}

question_topics = """

Note: If the student has mastered most skills, the complex numerical reasoning problems under advanced arithmetic and the geometry/trigonometry challenge problems under geometry are good options.

1. Data Analysis: Frequency Tables, Data Inference, Missing Number Given Average, Measures of Center, Measures of Spread
2. Quadratics: Discriminant, Quadratic Formula, Factoring, Remainder Theorem, Vertex from factored form, standard form, and vertex form, Vieta's Formula (Sum of Roots)
3. Geometry: Triangle Sum Theorem, Special Triangles, Area and Volume, Parallel lines and a transversal, Pythagorean Theorem, Congruence Proofs (SAS, ASA, SSS, AAS), Arcs and Central Angles, Similar Triangles, Equation of a Circle, Distance Formula, Midpoint Formula, Geometry and Trigonometry Challenge Problems
4. Linear Equations: Linear Relationship Word Problems, Interpreting Linear Equations, Equation from two points (function notation), Slopes of Parallel/Perpendicular Lines
5. Algebra: Solve one step equation, Solve multi step equation, Algebraic Inequalities, Proportional expressions
6. Terminology: Math Vocabulary such as integer, rational number, irrational number, prime number, composite number, factor, multiple, etc.
7. Arithmetic: Fractions, Combining Like Terms, Exponent Properties, Percents, Box/FOIL, F(x) notation, Evaluation, Percent Increase/Decrease
8. Advanced Arithmetic: Expanding radicals, Dimensional analysis and unit conversions, Imaginary numbers, Polynomial Long Division, Completing the Square, Rational Roots Theorem, Missing Number Given Average, , Complex Numerical Reasoning/Challenge Problems
9. Exponential Equations: Linear vs. Exponential, Word Problem to Equation
10. Systems: Desmos problem, Intersection points and solutions, Word Problems
11. Trigonometry: Trig Ratios, Radian/Degree Conversions
12. Proportional Reasoning: A-List Math Fundamentals Type
13. Probability: From a table, 'and', 'or'
14. Nonlinear Functions: Local extrema and intercepts from graphs
15. Intercepts: From multiple equation types
16. Reading and Writing: Command of textual evidence, sentence boundaries, grammar, command of quantitative evidence given a table or graph, words in context, and expression of ideas
"""

def determine_exact_question_type(topic_description: str, need_description: str) -> str:
    # OpenAI API Key (replace with your actual key)
    prompt = f"""
    Given this need description: {need_description}, use this topic description: {topic_description} to determine the exact quesiton type that is needed. 
    Respond with only the number of the question type from the list of topic descriptions.
    Respond with "Other" if no question type suffices.
    """
  

    response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=150,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
)

    # Extract and return the relevant question types from the response
    question_type = response.choices[0].message.content

    return question_type

def determine_question_type(need_description: str, question_topics: dict) -> list:
    # OpenAI API Key (replace with your actual key)

    prompt = f"""
    Given this need description: {need_description}, use this list of topics: {question_topics} to determine the question topic that is needed. 
    If it is apparent that the student needs to practice multiple skills, provide the most foundational topic.  For example, a student should not practice algebra if they have not mastered arithmetic.
    Respond with only the number of the question topic from the list of topics.
    Respond with "Other" if no question topic suffices.
    """
    
    response = client.chat.completions.create(
                model="gpt-4o-mini",
                max_tokens=150,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
)
    topic_number = response.choices[0].message.content

    if topic_number == "Other":
        
        return "Other", "Other"

    int_num = int(topic_number)

    #pass topic_descriptions[topic number - 1] to get_exact
    question_type = determine_exact_question_type(question_descriptions[int_num - 1], need_description)

    question_typenum_within_topic = int(question_type)
    
    
    return topic_number, question_typenum_within_topic

def retrieve_qb_question(need_description:str, user_id: int, db: Session):
       

    topic_number, question_typenum_within_topic = determine_question_type(need_description, question_topics)
    print(f"question type found with coordinates: {int(topic_number), question_typenum_within_topic}")

    if topic_number == "Other":
        
        return "Other"


    # logic for mapping LLM response to actual question type names in DB
    question_type = question_mapping[int(topic_number)][question_typenum_within_topic]

    question_type_id = db.query(QuestionType).filter(QuestionType.question_type_name == question_type).first().question_type_id
    print("question id found")

    #avoid repeat questions: logic for determining which question number the user is on for that type by querying DB
    progress_record = get_user_progress_on_question_type(db, user_id, question_type_id)
    print(f"the user is on question {progress_record + 1}")

    if progress_record:
        print(f"User {user_id} is on question number {progress_record + 1} for question type {question_type_id}.")
    else:
        print(f"No progress record found for user {user_id} on question type {question_type_id}.")


   #increment user progress
    increment_user_progress(db, user_id, question_type)


    #query db for question
    question = get_question_by_sub_topic_and_number(db, question_type, progress_record + 1)
    print("question metadata retrieved")


    return question

def retrieve_pt_question(need_description:str, user_id: int, db: Session):
    #logic
    
    question = PracticeTestQuestion().get_random_question()


    #logic for displaying question to user




    return question

def web_search(query):
    ddgs = DDGS()
    results = ddgs.text(query, max_results=5)
    return "\n".join([result['snippet'] for result in results])

known_actions = {
    "retrieve_qb_question": retrieve_qb_question,
    "retrieve_pt_question": retrieve_pt_question,
    "search the web": web_search
  
}

action_re = re.compile('^Action: (\w+): (.*)$')   # python regular expression to selection action

def query_agent(messages, user_id: UUID, db, max_turns=3):
    i = 0
    print("agent queried")
    bot = Agent()
    print("agent created")
    next_prompt = messages
    observation = None  
    while i < max_turns:
        i += 1
        result = bot(next_prompt)
        print(result)
        actions = [
            action_re.match(a) 
            for a in result.split('\n') 
            if action_re.match(a)
        ]
        if actions:
            print("action found")
            # There is an action to run
            action, action_input = actions[0].groups()
            if action not in known_actions:
                raise Exception("Unknown action: {}: {}".format(action, action_input, user_id, db))
            print(" -- running {} {}".format(action, action_input, user_id, db))
            observation = known_actions[action](action_input, user_id, db) # execute the action and store in observation
            print("Observation:", observation)
            next_prompt = "Observation: {}".format(observation)
        else:
            print("no further action found")
            result = result.replace("Answer:", "")
            return result, observation


# # gpt4o, pip install openai==0.28
# def generate_new_response(messages):
#   response = openai.ChatCompletion.create(
#     model="gpt-4o",
#     messages=messages
#   )
#   return response['choices'][0]['message']['content']










