def calculate_change(bill_denominations, total_purchase, paid_amount):
    """
    Calculate change using a greedy approach with Indonesian Rupiah denominations.
    
    Args:
    bill_denominations (list): List of available bill/coin denominations in descending order
    total_purchase (int): Total cost of purchase
    paid_amount (int): Amount paid by the customer
    
    Returns:
    dict: A dictionary of change denominations and their counts
    """
    # Calculate the change amount
    change = paid_amount - total_purchase
    
    # If no change is needed or insufficient payment
    if change < 0:
        raise ValueError("Insufficient payment amount")
    
    # Dictionary to store change breakdown
    change_breakdown = {}
    
    # Greedy approach to give maximum possible larger denominations first
    for denomination in bill_denominations:
        # How many of this denomination can be used
        count = change // denomination
        
        if count > 0:
            # Add to change breakdown
            change_breakdown[denomination] = count
            
            # Reduce the remaining change
            change %= denomination
        
        # If no change left, break the loop
        if change == 0:
            break
    
    return change_breakdown

def print_change(change_breakdown):
    """
    Print the change breakdown in a readable format.
    
    Args:
    change_breakdown (dict): Dictionary of change denominations and counts
    """
    print("\nChange Breakdown:")
    for denomination, count in change_breakdown.items():
        print(f"Rp {denomination:,} x {count}")

def main():
    # Available denominations in Indonesian Rupiah (from largest to smallest)
    bill_denominations = [
        100000, 50000, 20000, 10000, 5000, 
        2000, 1000, 500, 200, 100
    ]
    
    # Get user input
    total_purchase = int(input("Enter total purchase amount: "))
    paid_amount = int(input("Enter amount paid: "))
    
    try:
        # Calculate change
        change_breakdown = calculate_change(bill_denominations, total_purchase, paid_amount)
        
        # Print results
        print(f"\nTotal Purchase: Rp {total_purchase:,}")
        print(f"Amount Paid: Rp {paid_amount:,}")
        print(f"Total Change: Rp {paid_amount - total_purchase:,}")
        
        print_change(change_breakdown)
    
    except ValueError as e:
        print(f"Error: {e}")

# Allow the script to be run directly or imported as a module
if __name__ == "__main__":
    main()