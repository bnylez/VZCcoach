# response_builder.py

class ResponseBuilder:
    def __init__(self, calc_results):
        """
        :param calc_results: A dictionary containing all the metrics from the QuotaCalculator.
        Expected keys include: time, phone, internet, combined, revenue, averages.
        """
        self.results = calc_results

    def build_response(self):
        # Extract time variables
        current_day = self.results["time"]["current_day"]
        total_days = self.results["time"]["total_days"]
        days_remaining = self.results["time"]["days_remaining"]

        # Extract phone adds calculations
        phone = self.results["phone"]
        internet = self.results["internet"]
        combined = self.results["combined"]
        revenue = self.results["revenue"]
        averages = self.results["averages"]

        # Construct Email Subject (you could adjust as needed)
        subject = f"Daily Sales Coaching Report – Day {current_day}/{total_days}"

        # Build the email body with formatted text using the calculated values.
        body = f"""
Good Morning,

Here is your daily coaching report based on the performance metrics and targets as of Day {current_day} out of {total_days} (with {days_remaining} days remaining).

---------------------------------------------------------
1. Time & Performance Overview:
---------------------------------------------------------
- Current Day: {current_day}
- Total Days in Period: {total_days}
- Days Remaining: {days_remaining}

---------------------------------------------------------
2. Phone Adds (Counts):
---------------------------------------------------------
- Base Phone Adds Target: {phone["phone_target_count"]:.1f} counts
- Phone Adds Achieved: {phone["phone_achieved_count"]:.1f} counts
- Remaining Phone Adds Needed: {phone["remaining_phone"]:.1f} counts
- Daily Phone Adds Required (1.0 Bucket): {phone["daily_phone_target_1_0"]:.2f} adds/day
- Daily Phone Adds Required (Stretch 1.3 Bucket): {phone["daily_phone_target_1_3"]:.2f} adds/day

Insight: You've been averaging {averages["current_phone_avg"]:.2f} phone adds per day. Adjust your focus accordingly to meet your base or stretch targets.

---------------------------------------------------------
3. Internet (FWA) Adds (Counts):
---------------------------------------------------------
- Base Internet Adds Target: {internet["internet_target_count"]:.1f} counts
- Internet Adds Achieved: {internet["internet_achieved_count"]:.1f} counts
- Remaining Internet Adds Needed: {internet["remaining_internet"]:.1f} counts
- Daily Internet Adds Required (1.0 Bucket): {internet["daily_internet_target_1_0"]:.2f} adds/day
- Daily Internet Adds Required (Stretch 1.3 Bucket): {internet["daily_internet_target_1_3"]:.2f} adds/day

Insight: Your FWA performance is on track. Aim for the higher stretch target if bonus incentives are a priority.

---------------------------------------------------------
4. Combined Adds (Phone + Internet) (Counts):
---------------------------------------------------------
- Combined Target (1.0): {combined["combined_target"]:.1f} counts
- Combined Achieved: {combined["combined_achieved"]:.1f} counts
- Remaining Combined Adds Needed: {combined["remaining_combined"]:.1f} counts
- Daily Combined Adds Required (1.0 Bucket): {combined["daily_combined_target_1_0"]:.2f} adds/day
- Daily Combined Adds Required (Stretch 1.3 Bucket): {combined["daily_combined_target_1_3"]:.2f} adds/day

Insight: Your combined adds average is {averages["current_combined_avg"]:.2f} per day. Consider bundling offers to boost both phone and internet activations.

---------------------------------------------------------
5. Revenue Targets:
---------------------------------------------------------
- Sales Dollar Quota: ${revenue["revenue_quota"]:.2f}
- Sales Dollar Attainment: ${revenue["revenue_achieved"]:.2f}
- Remaining Revenue Needed: ${revenue["remaining_revenue"]:.2f}
- Daily Revenue Required (1.0 Bucket): ${revenue["daily_revenue_target_1_0"]:.2f} per day
- Daily Revenue Required (Stretch 1.3 Bucket): ${revenue["daily_revenue_target_1_3"]:.2f} per day

Insight: Your current revenue average is ${averages["current_revenue_avg"]:.2f} per day. Maintain or exceed this to drive higher multipliers.

---------------------------------------------------------
6. Overall Coaching Recommendations:
---------------------------------------------------------
- **Focus on Phone Adds:** You need to average approximately {phone["daily_phone_target_1_0"]:.2f} adds per day to meet the base target or {phone["daily_phone_target_1_3"]:.2f} for stretch. Consider prioritizing calls that convert into phone add dollars.
- **Boost Internet Activations:** With a target of {internet["daily_internet_target_1_0"]:.2f} adds for base and {internet["daily_internet_target_1_3"]:.2f} for stretch, increase your emphasis on home internet upsells if the opportunity arises.
- **Combined Strategy:** Optimizing your bundle offers could help meet the combined target, given your current combined adds average of {averages["current_combined_avg"]:.2f} per day.
- **Revenue Push:** Given the current revenue performance, continue to leverage high-margin products and upsell to maximize your earnings.
  
Keep pushing, and stay focused on the most critical gap areas. Your efforts today will set the pace for a successful period!

Best regards,
Your Daily Commission Coach Bot
        """
        return subject, body
