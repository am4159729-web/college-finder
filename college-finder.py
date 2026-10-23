import json
import os
from google import genai
from google.genai import types

client = genai.Client()


def find_colleges(user_data: dict) -> dict:
    system_instruction = """
    You are an expert university admissions and financial advisor.
    Analyze the student's profile, including subject GPAs, major, optional minor, family income, 
    ranked priorities (1 is highest priority), and extracurricular activities.

    Recommend 6 to 9 colleges divided into 3 categories: Reach, Target, Safety.

    Output MUST strictly follow this JSON schema:
    {
      "match_summary": "Brief analysis of profile strength.",
      "colleges": [
        {
          "name": "University Name",
          "category": "Reach | Target | Safety",
          "location": "City, State",
          "estimated_annual_cost_after_aid": "$XX,XXX",
          "admission_likelihood": "High | Moderate | Low",
          "why_it_fits": "Detailed reason matching top priorities",
          "financial_notes": "Context based on family income"
        }
      ]
    }
    """

    priorities_formatted = "\n".join(
        [
            f"        {idx + 1}. {p}"
            for idx, p in enumerate(user_data.get("priorities", []))
        ]
    )

    prompt = f"""
    Please evaluate this student profile and generate university recommendations:

    - Subject-Wise GPAs: {json.dumps(user_data.get('subject_gpas'))}
    - Intended Major: {user_data.get('major')}
    - Intended Minor: {user_data.get('minor', 'N/A')}
    - Annual Family Income: ${user_data.get('family_income', 0):,}
    - Ranked Priorities (1 = Highest):
{priorities_formatted}
    - Extracurricular Activities: {user_data.get('extracurriculars', 'N/A')}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            temperature=0.3,
        ),
    )

    return json.loads(response.text)


def collect_student_input() -> dict:
    print("=== COLLEGE FINDER AI: STUDENT PROFILE SETUP ===\n")

    print("--- 1. SUBJECT GPAs (0.0 - 4.0) ---")
    subjects = ["Math", "Science", "English", "History/Social Studies"]
    subject_gpas = {}
    for sub in subjects:
        while True:
            try:
                gpa_val = float(input(f"Enter {sub} GPA: "))
                if 0.0 <= gpa_val <= 4.0:
                    subject_gpas[sub] = gpa_val
                    break
                else:
                    print("Please enter a value between 0.0 and 4.0.")
            except ValueError:
                print("Invalid input. Please enter a valid number (e.g. 3.8).")

    print("\n--- 2. ACADEMIC INTERESTS ---")
    major = input("Enter Intended Major: ").strip()
    minor = input("Enter Intended Minor (Press Enter to skip/None): ").strip()
    if not minor:
        minor = "None"

    print("\n--- 3. FINANCIAL INFORMATION ---")
    while True:
        try:
            income_input = input("Enter Estimated Annual Family Income ($): ").replace(",", "").strip()
            family_income = float(income_input)
            break
        except ValueError:
            print("Invalid input. Please enter a number (e.g. 65000).")

    print("\n--- 4. RANK YOUR TOP 5 PRIORITIES ---")
    print("Examples: Low Tuition, High Major Ranking, Urban Location, Research Opportunities, Sports")
    priorities = []
    for i in range(1, 6):
        p = input(f"Rank #{i} Priority: ").strip()
        if not p:
            p = f"Priority {i}"
        priorities.append(p)

    print("\n--- 5. EXTRACURRICULAR ACTIVITIES ---")
    extracurriculars = input("Enter Extracurriculars/Clubs/Volunteering (Press Enter for N/A): ").strip()
    if not extracurriculars:
        extracurriculars = "N/A"

    return {
        "subject_gpas": subject_gpas,
        "major": major,
        "minor": minor,
        "family_income": family_income,
        "priorities": priorities,
        "extracurriculars": extracurriculars,
    }


if __name__ == "__main__":
    student_input = collect_student_input()

    print("\nConnecting to Gemini AI and analyzing profile...")
    results = find_colleges(student_input)

    print(f"\n--- PROFILE SUMMARY ---\n{results['match_summary']}\n")
    print("--- RECOMMENDED COLLEGES ---")

    for col in results["colleges"]:
        print(f"\n[{col['category'].upper()}] {col['name']} ({col['location']})")
        print(f"Est. Net Cost/Yr: {col['estimated_annual_cost_after_aid']}")
        print(f"Why It Fits: {col['why_it_fits']}")
        print(f"Financial Aid Note: {col['financial_notes']}")
