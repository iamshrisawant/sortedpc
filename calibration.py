from sentence_transformers import CrossEncoder

model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

pairs = [
    # Case: AWS Bill
    ("AWS Invoice. Compute instances: $400. Please pay by card.", "Work"),
    ("AWS Invoice. Compute instances: $400. Please pay by card.", "Finance"),
    
    # Case: Python Finance Code
    ("def calculate_compound_interest(p, r, t): return p * (1 + r/n)**(n*t)", "Work"),
    ("def calculate_compound_interest(p, r, t): return p * (1 + r/n)**(n*t)", "Engineering"),
    ("def calculate_compound_interest(p, r, t): return p * (1 + r/n)**(n*t)", "Medical"),
]

scores = model.predict(pairs)

print("--- Calibration Scores (Raw Logits) ---")
for (txt, ctx), score in zip(pairs, scores):
    print(f"Ctx: '{ctx}' | Score: {score:.4f}")
