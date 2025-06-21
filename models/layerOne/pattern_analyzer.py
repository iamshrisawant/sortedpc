import re

def generalize_rules(rule_text):
    generalized = []
    for line in rule_text.split('\n'):
        if 'feature' in line:
            line = re.sub(r" <= \d+\.\d+", " <= [value]", line)
            line = re.sub(r" > \d+\.\d+", " > [value]", line)
        generalized.append(line)
    return "\n".join(generalized)

if __name__ == "__main__":
    with open("models/layer1/tree_rules.txt") as f:
        raw_rules = f.read()
    
    generalized = generalize_rules(raw_rules)

    with open("models/layer1/generalized_rules.txt", "w", encoding="utf-8") as f:
        f.write(generalized)
    
    print("Rules generalized and saved.")
