from simple_sparql_wrapper import SimpleDanceKG


if __name__ == "__main__":
    kg = SimpleDanceKG()

    print("Top 5 dance styles:")
    for i, row in enumerate(kg.top_dance_styles(limit=5), start=1):
        print(f"{i}. {row['styleName']}")

    style = input("\nEnter a dance style (exact name) to query: ").strip()
    if not style:
        print("No style entered. Exiting.")
        exit()

    # Dynamically collect filters
    filters = []
    try:
        n = int(input("How many filters do you want to apply? (0 for none): ").strip())
    except ValueError:
        n = 0

    for i in range(n):
        prop  = input(f"  Filter {i + 1} — property (e.g. dance:hardness): ").strip()
        value = input(f"  Filter {i + 1} — value    (e.g. beginner):         ").strip()
        if prop and value:
            filters.append((prop, value))

    print(f"\nResults for style: '{style}'" + (f" with {len(filters)} filter(s)" if filters else ""))
    rows = kg.dance_style_details(style, filters=filters, limit=10)

    if not rows:
        print("No records found.")
    else:
        for row in rows:
            print(row)
