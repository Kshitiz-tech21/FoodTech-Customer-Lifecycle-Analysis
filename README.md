# FoodTech Customer Lifecycle Analysis 🍔📈

An end-to-end SQL-based analytics project designed to evaluate the efficiency of a loyalty program (Gold Membership) on customer spending and retention patterns in a food-delivery ecosystem.

## 🎯 Business Objective
The goal of this analysis is to determine if the 'Gold Membership' program successfully increases the **Customer Lifetime Value (LTV)** and alters purchasing behavior. We specifically analyze the transition from a standard user to a loyalty member.

## 🛠️ Tech Stack
- **Database:** PostgreSQL / MySQL
- **Analysis:** SQL (CTEs, Window Functions, Joins)
- **Metrics:** LTV, Retention Rate, Cohort Behavior, ROI on Loyalty Points

## 🚀 Key Analysis Performed
- **LTV Calculation:** Aggregated total spend per user to identify high-value customers.
- **Behavioral Shift:** Compared purchase frequency and order value *before* vs *after* membership enrollment.
- **Onboarding Analysis:** Identified the most common "first-purchase" items to optimize new user welcome offers.
- **Loyalty ROI:** Modeled a points-based reward system to calculate potential liability and user engagement.

## 📈 Business Insights & Recommendations
- **Membership Impact:** Users typically show a $[X]% increase in order frequency after joining the Gold program.
- **Retention:** Gold members exhibit a higher retention rate compared to non-members, suggesting the program effectively reduces churn.
- **Recommendation:** Introduce a "Tiered Loyalty" system based on the observed spending patterns of the top 10% of users to further increase AOV.

## 📂 Project Structure
- `/sql`: Contains the full schema setup and analytical queries.
- `/python`: (Upcoming) Automation scripts for data extraction.
- `/docs`: Documentation on data dictionary and business logic.
