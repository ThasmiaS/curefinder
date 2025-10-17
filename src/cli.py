# src/cli.py
from queries import get_disease_info, predict_new_drugs
import json

def main():
    print("=== HetioNet CLI ===")
    while True:
        print("\n1) Query disease info\n2) Predict new drugs\nq) Quit")
        c = input("> ").strip()
        if c == "1":
            d = input("Enter disease id (e.g., Disease::DOID:263): ").strip()
            res = get_disease_info(d)
            print(json.dumps(res, indent=2))
        elif c == "2":
            res = predict_new_drugs()
            print("Predicted compound-disease pairs (sample):")
            for item in res[:20]:
                print(item)
        elif c.lower() == "q":
            break
        else:
            print("Unknown choice")

if __name__ == "__main__":
    main()

