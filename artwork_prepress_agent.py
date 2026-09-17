import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("StickerMulePrePressAgent")

@dataclass
class PrintJobSpec:
    job_id: str
    customer_email: str
    product_type: str  # e.g., 'die-cut-sticker', 'clear-sticker', 'acrylic-keychain'
    requested_width_inches: float
    requested_height_inches: float
    file_dpi: int
    has_cut_line: bool
    color_mode: str  # e.g., 'CMYK', 'RGB'

class PrePressAgent:
    """
    Autonomous AI Pre-Press Agent designed for Sticker Mule workflows.
    Evaluates uploaded artwork against production tolerances, detects vector/bleed
    issues, and outputs actionable pre-flight instructions.
    """

    MIN_REQUIRED_DPI = 300
    SUPPORTED_COLOR_MODES = ["CMYK", "RGB"]

    def __init__(self, agent_name: str = "PrePress-Inspector-V1"):
        self.agent_name = agent_name
        logger.info(f"Initialized {self.agent_name}")

    def analyze_job(self, job: PrintJobSpec) -> Dict[str, Any]:
        """
        Executes autonomous pre-flight inspection routines on incoming print jobs.
        """
        logger.info(f"Processing Job ID: {job.job_id} for product '{job.product_type}'...")
        
        flags: List[str] = []
        action_required: bool = False
        auto_fixable: bool = False

        # 1. Inspect Resolution (DPI)
        if job.file_dpi < self.MIN_REQUIRED_DPI:
            flags.append(f"Low resolution detected ({job.file_dpi} DPI). Minimum required is {self.MIN_REQUIRED_DPI} DPI.")
            action_required = True
            auto_fixable = True  # Vectorization/Upscaling tool can process this

        # 2. Check Cut Line / Bleed Layer
        if not job.has_cut_line:
            flags.append("Missing cut line path. Auto-generating custom die-cut outline offset.")
            auto_fixable = True

        # 3. Check Color Space
        if job.color_mode.upper() == "RGB":
            flags.append("RGB color profile detected. Auto-converting to CMYK for accurate print representation.")
            auto_fixable = True

        # Determine overall decision path
        if not flags:
            status = "APPROVED_FOR_PRINT"
            recommended_action = "Route directly to printing pipeline."
        elif auto_fixable and len(flags) <= 2:
            status = "AUTO_FIX_APPLIED"
            recommended_action = "Generated vector proof automatically. Send proof to customer for instant approval."
        else:
            status = "NEEDS_HUMAN_REVIEW"
            recommended_action = "Escalate to pre-press support specialist."

        decision_payload = {
            "agent": self.agent_name,
            "job_id": job.job_id,
            "product_type": job.product_type,
            "status": status,
            "detected_issues": flags,
            "recommended_action": recommended_action,
            "dimensions": f"{job.requested_width_inches}\" x {job.requested_height_inches}\"",
        }

        return decision_payload

# Driver execution for demonstration
if __name__ == "__main__":
    # Test Case 1: Artwork needing auto-vectorization & cut-line generation
    sample_job = PrintJobSpec(
        job_id="SM-90210",
        customer_email="client@example.com",
        product_type="die-cut-sticker",
        requested_width_inches=3.0,
        requested_height_inches=3.0,
        file_dpi=150,  # Below threshold
        has_cut_line=False,
        color_mode="RGB"
    )

    agent = PrePressAgent()
    result = agent.analyze_job(sample_job)

    print("\n--- AGENT INSPECTION RESULT ---")
    print(json.dumps(result, indent=2))
