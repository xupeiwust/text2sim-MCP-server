"""
Statistical analysis module for multiple simulation replications.
Provides statistical reporting for simulation results.
"""

import statistics
import math
from typing import Dict, List, Any, Optional
from scipy import stats
import numpy as np


class ReplicationAnalyzer:
    """Analyzes multiple simulation replications with industry-standard statistics."""
    
    def __init__(self, confidence_levels: List[float] = [0.90, 0.95, 0.99]):
        """
        Initialize the replication analyzer.
        
        Args:
            confidence_levels: List of confidence levels to calculate (default: 90%, 95%, 99%)
        """
        self.confidence_levels = confidence_levels
    
    def analyze_replications(self, replications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform comprehensive statistical analysis on multiple replications.
        
        Args:
            replications: List of simulation results from individual replications
            
        Returns:
            Dict containing comprehensive statistical analysis
        """
        if not replications:
            raise ValueError("No replications provided for analysis")
        
        if len(replications) < 2:
            raise ValueError("At least 2 replications required for statistical analysis")
        
        # Extract all numeric metrics from replications
        metrics = self._extract_metrics(replications)
        
        # Perform statistical analysis for each metric
        analysis_results = {}
        for metric_name, values in metrics.items():
            if len(values) >= 2:  # Need at least 2 values for statistics
                analysis_results[metric_name] = self._analyze_metric(metric_name, values)
        
        # Add overall replication summary
        analysis_results["_replication_summary"] = {
            "total_replications": len(replications),
            "successful_replications": len([r for r in replications if "_metadata" not in r or "error" not in r]),
            "metrics_analyzed": len(analysis_results),
            "confidence_levels": self.confidence_levels
        }
        
        # Add individual replication data for transparency
        analysis_results["_individual_replications"] = replications
        
        return analysis_results
    
    def _extract_metrics(self, replications: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract all numeric metrics from replications."""
        metrics = {}
        
        for replication in replications:
            for key, value in replication.items():
                # Skip metadata and non-numeric values
                if key.startswith("_") or not isinstance(value, (int, float)):
                    continue
                
                if key not in metrics:
                    metrics[key] = []
                metrics[key].append(float(value))
        
        return metrics
    
    def _analyze_metric(self, metric_name: str, values: List[float]) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis on a single metric."""
        n = len(values)
        
        # Basic statistics
        mean_val = statistics.mean(values)
        median_val = statistics.median(values)
        std_dev = statistics.stdev(values) if n > 1 else 0.0
        variance = statistics.variance(values) if n > 1 else 0.0
        
        # Range and percentiles
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val
        
        # Calculate percentiles
        percentiles = {}
        for p in [5, 10, 25, 75, 90, 95]:
            percentiles[f"p{p}"] = np.percentile(values, p)
        
        # Coefficient of variation (only for positive means)
        cv = (std_dev / abs(mean_val)) if mean_val != 0 else float('inf')
        
        # Standard error of mean
        se_mean = std_dev / math.sqrt(n) if n > 1 else 0.0
        
        # Confidence intervals
        confidence_intervals = {}
        for conf_level in self.confidence_levels:
            if n > 1:
                # Use t-distribution for small samples
                alpha = 1 - conf_level
                t_critical = stats.t.ppf(1 - alpha/2, n - 1)
                margin_of_error = t_critical * se_mean
                
                confidence_intervals[f"ci_{int(conf_level*100)}"] = {
                    "lower": mean_val - margin_of_error,
                    "upper": mean_val + margin_of_error,
                    "half_width": margin_of_error,
                    "relative_precision": (margin_of_error / abs(mean_val)) if mean_val != 0 else float('inf')
                }
        
        # Normality test (Shapiro-Wilk for n <= 50, otherwise skip)
        normality_test = None
        if 3 <= n <= 50:
            try:
                stat, p_value = stats.shapiro(values)
                normality_test = {
                    "test": "Shapiro-Wilk",
                    "statistic": stat,
                    "p_value": p_value,
                    "is_normal": p_value > 0.05,
                    "interpretation": "Normal distribution" if p_value > 0.05 else "Non-normal distribution"
                }
            except:
                normality_test = {"test": "Shapiro-Wilk", "error": "Test failed"}
        
        # Outlier detection (IQR method)
        q1 = percentiles["p25"]
        q3 = percentiles["p75"]
        iqr = q3 - q1
        outlier_bounds = {
            "lower": q1 - 1.5 * iqr,
            "upper": q3 + 1.5 * iqr
        }
        outliers = [v for v in values if v < outlier_bounds["lower"] or v > outlier_bounds["upper"]]
        
        return {
            # Central tendency
            "mean": mean_val,
            "median": median_val,
            "mode": statistics.mode(values) if len(set(values)) < len(values) else None,
            
            # Variability
            "std_dev": std_dev,
            "variance": variance,
            "coefficient_of_variation": cv,
            "range": range_val,
            "min": min_val,
            "max": max_val,
            "iqr": iqr,
            
            # Percentiles
            "percentiles": percentiles,
            
            # Confidence intervals
            "confidence_intervals": confidence_intervals,
            
            # Sample statistics
            "sample_size": n,
            "degrees_of_freedom": n - 1,
            "standard_error": se_mean,
            
            # Distribution analysis
            "normality_test": normality_test,
            "outliers": {
                "count": len(outliers),
                "values": outliers,
                "bounds": outlier_bounds
            }
        }
    
    def format_industry_summary(self, analysis: Dict[str, Any]) -> str:
        """Format results in industry-standard reporting format."""
        summary_lines = []
        summary_lines.append("SIMULATION REPLICATION ANALYSIS SUMMARY")
        summary_lines.append("=" * 50)
        
        repl_summary = analysis.get("_replication_summary", {})
        summary_lines.append(f"Total Replications: {repl_summary.get('total_replications', 'N/A')}")
        summary_lines.append(f"Successful Runs: {repl_summary.get('successful_replications', 'N/A')}")
        summary_lines.append("")
        
        # Format each metric
        for metric_name, metric_data in analysis.items():
            if metric_name.startswith("_"):
                continue
                
            summary_lines.append(f"{metric_name.replace('_', ' ').title()}:")
            
            # Industry standard format: Mean ± Half-Width (CI%) [n=replications]
            mean = metric_data.get("mean", 0)
            ci_95 = metric_data.get("confidence_intervals", {}).get("ci_95", {})
            half_width = ci_95.get("half_width", 0)
            sample_size = metric_data.get("sample_size", 0)
            
            if half_width > 0:
                summary_lines.append(f"  {mean:.4f} ± {half_width:.4f} (95%) [n={sample_size}]")
            else:
                summary_lines.append(f"  {mean:.4f} [n={sample_size}]")
            
            # Additional statistics
            std_dev = metric_data.get("std_dev", 0)
            cv = metric_data.get("coefficient_of_variation", 0)
            min_val = metric_data.get("min", 0)
            max_val = metric_data.get("max", 0)
            
            summary_lines.append(f"  Std Dev: {std_dev:.4f}, CV: {cv:.2%}")
            summary_lines.append(f"  Range: [{min_val:.4f}, {max_val:.4f}]")
            
            # Relative precision
            rel_precision = ci_95.get("relative_precision", 0)
            if rel_precision < float('inf'):
                summary_lines.append(f"  Relative Precision: ±{rel_precision:.1%}")
            
            summary_lines.append("")
        
        return "\n".join(summary_lines)


def create_replication_analyzer() -> ReplicationAnalyzer:
    """Factory function to create a replication analyzer with default settings."""
    return ReplicationAnalyzer()
