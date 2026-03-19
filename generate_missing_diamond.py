from diamond_generator import generate_diamond_report

def main():
    # California Injury Law
    lead_id = 'f5df9c2f-d168-4dfe-81f5-202428fda03b'
    print(f"Generating Diamond Report for target: {lead_id}...")
    report_path = generate_diamond_report(lead_id)
    if report_path:
        print(f"SUCCESS: Report saved at {report_path}")
    else:
        print("FAILED to generate report.")

if __name__ == "__main__":
    main()
