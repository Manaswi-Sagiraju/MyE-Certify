from sqlmodel import Session, select
from .models import CertificateRecord


def seed_data(session: Session) -> None:
	# Only seed if empty
	count = session.exec(select(CertificateRecord)).first()
	if count:
		return

	session.add_all(
		[
			CertificateRecord(
				institution_id="UoJ-01",
				certificate_id="CERT-2023-0001",
				candidate_name="Alice",
				roll_number="RJH12345",
				course="B.Sc Computer Science",
				year=2023,
			),
			CertificateRecord(
				institution_id="UoJ-02",
				certificate_id="CERT-2022-0099",
				candidate_name="Bob",
				roll_number="RJH98765",
				course="MBA",
				year=2022,
			),
		]
	)
	session.commit()


