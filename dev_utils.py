# # MODEL TO DB
from sqlalchemy import create_engine
from app.database.base import Base
from app.models import *  # This imports all models
from app.database.session import get_db as db  # Assuming the database session function exists
from sqlalchemy.orm import sessionmaker
from app.database.config import engine




# # MODEL TO DB
# from sqlalchemy import create_engine
# from app.database.base import Base
# from app.models import *  # This imports all models

# DATABASE_URL = "postgresql://cameronhightower:Wellpleased22!@localhost:5432/automated_tutoring_service"
# engine = create_engine(DATABASE_URL, echo=True)  # Set echo to True to log SQL queries
# Base.metadata.create_all(engine)





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

# def populate_question_types(db_session):
#     for question_type_name in types:
#         # Check if the question type already exists
#         existing_question_type = db_session.query(QuestionType).filter_by(question_type_name=question_type_name).first()
        
#         if not existing_question_type:
#             # If it doesn't exist, create a new record
#             new_question_type = QuestionType(question_type_name=question_type_name)
#             db_session.add(new_question_type)
    
#     # Commit the changes to the database
#     db_session.commit()

# # Create a session and populate the table
# Session = sessionmaker(bind=engine)
# session = Session()

# populate_question_types(session)

# session.close()
