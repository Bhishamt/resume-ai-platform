from typing import Dict, List

class ScoreCalculator:
    @classmethod
    def calculate_similarity_score(cls, similarity: float) -> tuple[int, float, List[Dict]]:
        """Calculate similarity score out of 100 and weighted score out of 10.
        
        Returns:
            tuple[score_out_of_100, weighted_score, reasons]
        """
        category_score = similarity * 100.0
        weighted_score = similarity * 10.0
        
        reasons = []
        reasons.append({"rule": f"Cosine text similarity is {int(round(category_score))}%", "points": 0.0})
        
        if category_score < 80.0:
            # Let's say if similarity is below 80% we explain the deduction relative to max of 10 points
            deduction = 10.0 - weighted_score
            reasons.append({"rule": "Text similarity below 80% benchmark", "points": -round(deduction, 2)})
            
        return int(round(category_score)), round(weighted_score, 2), reasons

    @classmethod
    def calculate_overall_match(cls, category_weighted_scores: Dict[str, float]) -> int:
        """Calculate final overall match percentage by summing category weights."""
        total = sum(category_weighted_scores.values())
        return max(0, min(100, int(round(total))))
