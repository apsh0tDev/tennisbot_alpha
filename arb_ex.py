# Simulated data for testing
matches = [
    {"match": "Match 1", "bookmaker1": {"playerA": 2.10, "playerB": 1.80}, "bookmaker2": {"playerA": 2.20, "playerB": 1.75}},
    {"match": "Match 2", "bookmaker1": {"playerA": 1.95, "playerB": 2.00}, "bookmaker2": {"playerA": 2.05, "playerB": 1.90}},
    {"match": "Match 3", "bookmaker1": {"playerA": 1.85, "playerB": 2.15}, "bookmaker2": {"playerA": 1.90, "playerB": 2.10}},
    {"match": "Match 4", "bookmaker1": {"playerA": 2.30, "playerB": 1.70}, "bookmaker2": {"playerA": 2.25, "playerB": 1.75}},
    {"match": "Match 5", "bookmaker1": {"playerA": 2.00, "playerB": 1.90}, "bookmaker2": {"playerA": 1.95, "playerB": 1.95}},
    {"match": "Match 6", "bookmaker1": {"playerA": 2.50, "playerB": 1.60}, "bookmaker2": {"playerA": 2.45, "playerB": 1.65}},
    {"match": "Match 7", "bookmaker1": {"playerA": 2.40, "playerB": 1.65}, "bookmaker2": {"playerA": 2.35, "playerB": 1.70}},
    {"match": "Match 8", "bookmaker1": {"playerA": 2.55, "playerB": 1.57}, "bookmaker2": {"playerA": 2.50, "playerB": 1.60}},
    {"match": "Match 9", "bookmaker1": {"playerA": 1.88, "playerB": 2.05}, "bookmaker2": {"playerA": 1.92, "playerB": 2.00}},
    {"match": "Match 10", "bookmaker1": {"playerA": 2.00, "playerB": 1.85}, "bookmaker2": {"playerA": 2.05, "playerB": 1.80}},
    {"match": "Match 11", "bookmaker1": {"playerA": 2.70, "playerB": 1.50}, "bookmaker2": {"playerA": 2.60, "playerB": 1.55}},
    {"match": "Match 12", "bookmaker1": {"playerA": 1.75, "playerB": 2.25}, "bookmaker2": {"playerA": 1.80, "playerB": 2.20}},
    {"match": "Match 13", "bookmaker1": {"playerA": 2.10, "playerB": 1.80}, "bookmaker2": {"playerA": 2.05, "playerB": 1.85}},
    {"match": "Match 14", "bookmaker1": {"playerA": 1.70, "playerB": 2.30}, "bookmaker2": {"playerA": 1.75, "playerB": 2.25}},
    {"match": "Match 15", "bookmaker1": {"playerA": 2.20, "playerB": 1.78}, "bookmaker2": {"playerA": 2.18, "playerB": 1.80}},
    {"match": "Match 16", "bookmaker1": {"playerA": 2.35, "playerB": 1.68}, "bookmaker2": {"playerA": 2.32, "playerB": 1.70}},
    {"match": "Match 17", "bookmaker1": {"playerA": 2.45, "playerB": 1.60}, "bookmaker2": {"playerA": 2.40, "playerB": 1.62}},
    {"match": "Match 18", "bookmaker1": {"playerA": 1.90, "playerB": 2.00}, "bookmaker2": {"playerA": 1.92, "playerB": 1.98}},
    {"match": "Match 19", "bookmaker1": {"playerA": 2.55, "playerB": 1.58}, "bookmaker2": {"playerA": 2.50, "playerB": 1.60}},
    {"match": "Match 20", "bookmaker1": {"playerA": 2.60, "playerB": 1.55}, "bookmaker2": {"playerA": 2.55, "playerB": 1.58}},
]

# Function to calculate arbitrage
def calculate_arbitrage(matches):
    for match in matches:
        bookmaker1_playerA_odds = match['bookmaker1']['playerA']
        bookmaker1_playerB_odds = match['bookmaker1']['playerB']
        bookmaker2_playerA_odds = match['bookmaker2']['playerA']
        bookmaker2_playerB_odds = match['bookmaker2']['playerB']

        best_odds_playerA = max(bookmaker1_playerA_odds, bookmaker2_playerA_odds)
        best_odds_playerB = max(bookmaker1_playerB_odds, bookmaker2_playerB_odds)

        arbitrage_percentage = (1 / best_odds_playerA) + (1 / best_odds_playerB)

        if arbitrage_percentage < 1:
            total_stake = 100  # Example total stake for illustration
            stake_playerA = total_stake / best_odds_playerA
            stake_playerB = total_stake / best_odds_playerB
            potential_payout = total_stake / arbitrage_percentage
            guaranteed_profit = potential_payout - total_stake
            profit_percentage = (guaranteed_profit / total_stake) * 100

            print("/!\\Arbitrage Found/!\\")
            print(f"- Profit = {profit_percentage:.2f}%")
            print(f"- Match = {match['match']}")
            print(f"- Books = bookmaker1/bookmaker2")
            print(f"- Odds = {best_odds_playerA} | {best_odds_playerB}")
            print(f"- Stakes[{total_stake}$] = {stake_playerA:.2f}$ | {stake_playerB:.2f}$")
            print("- Date = Today")
        else:
            print(f"{match['match']}: No arbitrage opportunity found.")

# Run the function with the simulated data
calculate_arbitrage(matches)
