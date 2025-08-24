import pytest
from datetime import datetime
from gtfs_realtime_translators.translators.de_vvs import DeVVSAlertGtfsRealtimeTranslator


testdata= [
		("Vom 07.10.2024 bis 31.12.2025", "2024-10-07"),
		#  Not yet supported: ("1./2. und 2./3. September 2025", "2025-09-01"),
		("Ab Freitag, 11. April 2025", "2025-04-11"),
		("04. März 2025 bis Freitag, 30. April 2027", "2025-03-04"),
		# Not yet supported: ("9. September, 7. Oktober, 4. November und 2. Dezember 2025", "2025-09-09"),
	    # Not yet supported: ("8.-10. und 15.-17. November 2025", "2025-11-08"),
		("Aufgrund von Bauarbeiten kann die Haltestelle Marktplatz Rathaus am 25.07.2025 ab 10 Uhr bis ca. 20.12.2025", "2025-07-25")
	]


@pytest.mark.parametrize("input,expected", testdata)
def test_extract_beginning(input, expected):
	
	result = DeVVSAlertGtfsRealtimeTranslator.extract_impact_period_start(input)
	
	assert result == datetime.strptime(expected, '%Y-%m-%d')

