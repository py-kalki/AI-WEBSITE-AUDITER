class ScoreCalculator:
    def calculate(self, performance_data, seo_data, ux_data, mobile_data, broken_links_data):
        """Calculates the overall weighted score."""
        
        # Weights (can be adjusted)
        weights = {
            "performance": 0.25,
            "seo": 0.25,
            "ux": 0.20,
            "mobile": 0.20,
            "links": 0.10
        }
        
        p_score = performance_data.get("score", 0)
        s_score = seo_data.get("score", 0)
        u_score = ux_data.get("score", 0)
        m_score = mobile_data.get("score", 0)
        l_score = broken_links_data.get("score", 0)
        
        overall_score = (
            p_score * weights["performance"] +
            s_score * weights["seo"] +
            u_score * weights["ux"] +
            m_score * weights["mobile"] +
            l_score * weights["links"]
        )
        
        return int(overall_score)

    def get_priority_list(self, performance_data, seo_data, ux_data, mobile_data, broken_links_data):
        """Generates a priority list of improvements."""
        priorities = []
        
        # Performance
        if performance_data.get("score", 0) < 60:
            priorities.append({"category": "Performance", "priority": "High", "issue": "Website is too slow"})
            
        # SEO
        for issue in seo_data.get("issues", []):
            priorities.append({"category": "SEO", "priority": "Medium", "issue": issue})
            
        # UX
        for issue in ux_data.get("issues", []):
            priorities.append({"category": "UX", "priority": "Medium", "issue": issue})
            
        # Mobile
        for issue in mobile_data.get("issues", []):
            priorities.append({"category": "Mobile", "priority": "High", "issue": issue})
            
        # Links
        if broken_links_data.get("count", 0) > 0:
            priorities.append({"category": "Links", "priority": "Low", "issue": f"Fix {broken_links_data['count']} broken links"})
            
        return priorities
