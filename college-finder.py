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


student_input = {
    "subject_gpas": {
        "Math": 3.9,
        "Science": 3.8,
        "English": 3.2,
        "History/Social Studies": 3.4,
    },
    "major": "Computer Science",
    "minor": "None",
    "family_income": 65000,
    "priorities": [
        "Low Tuition Cost & Generous Financial Aid",
        "High Major/Department Ranking",
        "Urban / City Campus Location",
        "Undergraduate Research Opportunities",
        "Vibrant Campus Life & Sports Culture",
    ],
    "extracurriculars": "Robotics Team Lead (2 years), High School Swim Team, 80 Hours Volunteering at Local Library",
}

if __name__ == "__main__":
    results = find_colleges(student_input)

    print(f"\n--- PROFILE SUMMARY ---\n{results['match_summary']}\n")
    print("--- RECOMMENDED COLLEGES ---")

    for col in results["colleges"]:
        print(f"\n[{col['category'].upper()}] {col['name']} ({col['location']})")
        print(f"Est. Net Cost/Yr: {col['estimated_annual_cost_after_aid']}")
        print(f"Why It Fits: {col['why_it_fits']}")
        print(f"Financial Aid Note: {col['financial_notes']}")
