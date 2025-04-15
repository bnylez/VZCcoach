# calculator.py
import re

class QuotaCalculator:
    """
    This class computes daily targets and progress metrics for a sales rep
    based on a DataFrame of quota data and additional subject info.

    It uses the following fields from the DataFrame:
      - "EmailSubjectInfo": Expected to be in the form "Day 4/22"
      - "PhoneActivationsTarget": Dollar value for phone adds target (divide by 100 to get count)
      - "PhoneActivationsAchievement": Dollar value for phone adds achieved (divide by 100)
      - "FwaTarget": Dollar value for FWA (internet) adds target (divide by 100)
      - "FwaAchivement": Dollar value for FWA (internet) adds achieved (divide by 100)
      - "SalesDollarQuota": Revenue quota (in dollars)
      - "SalesDollarAttainment": Revenue achieved (in dollars)
    """
    def __init__(self, df):
        self.df = df
        self.subject_info = None
        if "EmailSubjectInfo" in self.df.columns:
            self.subject_info = self.df["EmailSubjectInfo"].iloc[0]
        self.current_day = None
        self.total_days = None
        self.days_remaining = None
        self._parse_subject_info()

    def _parse_subject_info(self):
        """
        Parses the subject info string, which is expected to be in the format: 
        "Day X/Y" where X is the current day and Y is the total number of days.
        Sets self.current_day, self.total_days, and self.days_remaining.
        """
        if not self.subject_info:
            # Default values if missing—assume day 1 of a 30-day period.
            self.current_day = 1
            self.total_days = 30
            self.days_remaining = self.total_days - self.current_day
            return

        # Look for pattern "Day X/Y"
        match = re.search(r"Day\s+(\d+)\s*/\s*(\d+)", self.subject_info, re.IGNORECASE)
        if match:
            self.current_day = int(match.group(1))
            self.total_days = int(match.group(2))
            self.days_remaining = self.total_days - self.current_day
        else:
            # Fallback default if pattern matching fails
            self.current_day = 1
            self.total_days = 30
            self.days_remaining = self.total_days - self.current_day

    def calculate_phone_adds(self):
        """
        Calculates phone add targets.
        Converts the provided dollar values to actual phone add counts by dividing by 100.
        Returns a dictionary with:
          - phone_target_count
          - phone_achieved_count
          - remaining_phone (count needed to hit target)
          - daily_phone_target_1_0 (daily adds needed for the base quota)
          - daily_phone_target_1_3 (daily adds needed for the 1.3 stretch target)
        """
        row = self.df.iloc[0]
        phone_target_dollars = row["PhoneActivationsTarget"]
        phone_achieved_dollars = row["PhoneActivationsAchievement"]

        phone_target_count = phone_target_dollars / 100.0
        phone_achieved_count = phone_achieved_dollars / 100.0
        remaining_phone = phone_target_count - phone_achieved_count

        daily_target_1_0 = remaining_phone / self.days_remaining if self.days_remaining > 0 else 0
        # Adjusted target for 1.3 bucket: increase by 30%
        adjusted_phone_target = 1.3 * phone_target_count
        daily_target_1_3 = (adjusted_phone_target - phone_achieved_count) / self.days_remaining if self.days_remaining > 0 else 0

        return {
            "phone_target_count": phone_target_count,
            "phone_achieved_count": phone_achieved_count,
            "remaining_phone": remaining_phone,
            "daily_phone_target_1_0": daily_target_1_0,
            "daily_phone_target_1_3": daily_target_1_3
        }

    def calculate_internet_adds(self):
        """
        Calculates internet (FWA) add targets.
        Converts FWA dollar values to counts (divide by 100).
        Returns a dictionary with:
          - internet_target_count
          - internet_achieved_count
          - remaining_internet
          - daily_internet_target_1_0 (for base quota)
          - daily_internet_target_1_3 (for stretch target)
        """
        row = self.df.iloc[0]
        fwa_target_dollars = row["FwaTarget"]
        fwa_achieved_dollars = row["FwaAchivement"]

        internet_target_count = fwa_target_dollars / 100.0
        internet_achieved_count = fwa_achieved_dollars / 100.0
        remaining_internet = internet_target_count - internet_achieved_count

        daily_target_1_0 = remaining_internet / self.days_remaining if self.days_remaining > 0 else 0
        adjusted_internet_target = 1.3 * internet_target_count
        daily_target_1_3 = (adjusted_internet_target - internet_achieved_count) / self.days_remaining if self.days_remaining > 0 else 0

        return {
            "internet_target_count": internet_target_count,
            "internet_achieved_count": internet_achieved_count,
            "remaining_internet": remaining_internet,
            "daily_internet_target_1_0": daily_target_1_0,
            "daily_internet_target_1_3": daily_target_1_3
        }

    def calculate_combined_adds(self):
        """
        Combines phone and internet adds by summing their respective counts.
        Returns a dictionary with:
          - combined_target: Sum of phone and internet targets (in counts)
          - combined_achieved: Sum of phone and internet adds achieved
          - remaining_combined: Count still needed to hit target
          - daily_combined_target_1_0: Required daily adds for base quota
          - daily_combined_target_1_3: Required daily adds for stretch quota
        """
        phone = self.calculate_phone_adds()
        internet = self.calculate_internet_adds()
        combined_target = phone["phone_target_count"] + internet["internet_target_count"]
        combined_achieved = phone["phone_achieved_count"] + internet["internet_achieved_count"]
        remaining_combined = combined_target - combined_achieved
        
        daily_target_1_0 = remaining_combined / self.days_remaining if self.days_remaining > 0 else 0
        adjusted_combined_target = 1.3 * combined_target
        daily_target_1_3 = (adjusted_combined_target - combined_achieved) / self.days_remaining if self.days_remaining > 0 else 0

        return {
            "combined_target": combined_target,
            "combined_achieved": combined_achieved,
            "remaining_combined": remaining_combined,
            "daily_combined_target_1_0": daily_target_1_0,
            "daily_combined_target_1_3": daily_target_1_3
        }

    def calculate_revenue(self):
        """
        Calculates revenue-based daily targets.
        Uses SalesDollarQuota and SalesDollarAttainment directly (in dollars).
        Returns a dictionary with:
          - revenue_quota
          - revenue_achieved
          - remaining_revenue (dollars needed)
          - daily_revenue_target_1_0: Daily revenue needed to hit the base quota
          - daily_revenue_target_1_3: Daily revenue needed for the 1.3 stretch target
        """
        row = self.df.iloc[0]
        revenue_quota = row["SalesDollarQuota"]
        revenue_achieved = row["SalesDollarAttainment"]
        remaining_revenue = revenue_quota - revenue_achieved
        
        daily_revenue_target_1_0 = remaining_revenue / self.days_remaining if self.days_remaining > 0 else 0
        adjusted_revenue_quota = 1.3 * revenue_quota
        daily_revenue_target_1_3 = (adjusted_revenue_quota - revenue_achieved) / self.days_remaining if self.days_remaining > 0 else 0

        return {
            "revenue_quota": revenue_quota,
            "revenue_achieved": revenue_achieved,
            "remaining_revenue": remaining_revenue,
            "daily_revenue_target_1_0": daily_revenue_target_1_0,
            "daily_revenue_target_1_3": daily_revenue_target_1_3
        }

    def calculate_current_averages(self):
        """
        Calculates current average counts and revenue per day based on days elapsed.
        Returns a dictionary with:
          - current_phone_avg
          - current_internet_avg
          - current_combined_avg
          - current_revenue_avg
        """
        row = self.df.iloc[0]
        days_elapsed = self.current_day if self.current_day > 0 else 1

        phone = self.calculate_phone_adds()
        internet = self.calculate_internet_adds()
        combined = phone["phone_achieved_count"] + internet["internet_achieved_count"]
        current_phone_avg = phone["phone_achieved_count"] / days_elapsed
        current_internet_avg = internet["internet_achieved_count"] / days_elapsed
        current_combined_avg = combined / days_elapsed

        revenue_achieved = row["SalesDollarAttainment"]
        current_revenue_avg = revenue_achieved / days_elapsed

        return {
            "current_phone_avg": current_phone_avg,
            "current_internet_avg": current_internet_avg,
            "current_combined_avg": current_combined_avg,
            "current_revenue_avg": current_revenue_avg
        }

    def calculate_all(self):
        """
        Runs all calculations and returns a comprehensive dictionary containing
        time variables, phone, internet, combined adds, revenue targets, and current averages.
        """
        results = {}
        results["time"] = {
            "current_day": self.current_day,
            "total_days": self.total_days,
            "days_remaining": self.days_remaining
        }
        results["phone"] = self.calculate_phone_adds()
        results["internet"] = self.calculate_internet_adds()
        results["combined"] = self.calculate_combined_adds()
        results["revenue"] = self.calculate_revenue()
        results["averages"] = self.calculate_current_averages()
        return results
