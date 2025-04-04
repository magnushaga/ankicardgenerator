import os
import sys
from urllib.parse import quote_plus
from core.check_database import check_database_structure

def main():
    """
    Main function to check the database structure
    """
    # Properly encode password with special characters
    password = quote_plus("H@ukerkul120700")
    connection_string = f"postgresql://postgres:{password}@db.wxisvjmhokwtjwcqaarb.supabase.co:5432/postgres"
    
    try:
        print("Starting database check...")
        
        # Check database structure
        results = check_database_structure(connection_string)
        
        # Print summary
        print("\n=== Database Check Summary ===")
        print(f"Missing tables: {len(results['missing_tables'])}")
        print(f"Extra tables: {len(results['extra_tables'])}")
        print(f"Column issues: {len(results['column_issues'])}")
        print(f"Foreign key issues: {len(results['fk_issues'])}")
        print(f"Index issues: {len(results['index_issues'])}")
        print(f"Empty tables: {len(results['empty_tables'])}")
        
        if (len(results['missing_tables']) == 0 and 
            len(results['column_issues']) == 0 and 
            len(results['fk_issues']) == 0 and 
            len(results['index_issues']) == 0):
            print("\n✅ Database structure matches the model definitions!")
            return 0
        else:
            print("\n⚠️ Database structure has issues that need to be addressed.")
            return 1
        
    except Exception as e:
        print(f"\nError during database check: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 