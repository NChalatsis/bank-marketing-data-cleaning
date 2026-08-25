"""Clean and split the bank marketing campaign dataset."""
from pathlib import Path
import numpy as np
import pandas as pd


INPUT_PATH = Path("data/raw/bank_marketing.csv")
OUTPUT_DIR = Path("data/processed")

MONTHS = {
    "jan": 1,
    "feb": 2,
    "mar": 3,
    "apr": 4,
    "may": 5,
    "jun": 6,
    "jul": 7,
    "aug": 8,
    "sep": 9,
    "oct": 10,
    "nov": 11,
    "dec": 12,
}


def clean_bank_marketing_data(
    input_path: Path,
    output_dir: Path,
) -> None:
    """Clean the source data and create three CSV files."""

    df = pd.read_csv(input_path)

    # Create and clean the client dataset
    client_columns = [
        "client_id",
        "age",
        "job",
        "marital",
        "education",
        "credit_default",
        "mortgage",
    ]

    client = df[client_columns].copy()

    client["job"] = client["job"].str.replace(
        ".",
        "_",
        regex=False,
    )

    education = client["education"].str.replace(
        ".",
        "_",
        regex=False,
    )

    client["education"] = education.mask(
        education.eq("unknown"),
        np.nan,
    )

    client["credit_default"] = (
        client["credit_default"].eq("yes")
    )

    client["mortgage"] = client["mortgage"].eq("yes")

    # Create and clean the campaign dataset
    campaign_columns = [
        "client_id",
        "number_contacts",
        "contact_duration",
        "previous_campaign_contacts",
        "previous_outcome",
        "campaign_outcome",
        "month",
        "day",
    ]

    campaign = df[campaign_columns].copy()

    campaign["previous_outcome"] = (
        campaign["previous_outcome"].eq("success")
    )

    campaign["campaign_outcome"] = (
        campaign["campaign_outcome"].eq("yes")
    )

    month_number = campaign["month"].map(MONTHS)

    if month_number.isna().any():
        raise ValueError("Unsupported month value found")

    campaign["last_contact_date"] = pd.to_datetime(
        {
            "year": pd.Series(2022, index=campaign.index),
            "month": month_number,
            "day": campaign["day"],
        }
    )

    final_campaign_columns = [
        "client_id",
        "number_contacts",
        "contact_duration",
        "previous_campaign_contacts",
        "previous_outcome",
        "campaign_outcome",
        "last_contact_date",
    ]

    campaign = campaign[final_campaign_columns]

    # Create the economics dataset
    economics_columns = [
        "client_id",
        "cons_price_idx",
        "euribor_three_months",
    ]

    economics = df[economics_columns].copy()

    # Validate row counts and client IDs
    if not (
        len(client) == len(campaign) == len(economics)
    ):
        raise ValueError("Output row counts do not match")

    ids_aligned = (
        client["client_id"].equals(campaign["client_id"])
        and client["client_id"].equals(
            economics["client_id"]
        )
    )

    if not ids_aligned:
        raise ValueError(
            "Client IDs are not aligned across outputs"
        )

    # Create the output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export the cleaned datasets
    client.to_csv(
        output_dir / "client.csv",
        index=False,
    )

    campaign.to_csv(
        output_dir / "campaign.csv",
        index=False,
        date_format="%Y-%m-%d",
    )

    economics.to_csv(
        output_dir / "economics.csv",
        index=False,
    )

    print(
        "Created client.csv, campaign.csv, "
        "and economics.csv successfully."
    )


if __name__ == "__main__":
    clean_bank_marketing_data(
        input_path=INPUT_PATH,
        output_dir=OUTPUT_DIR,
    )
