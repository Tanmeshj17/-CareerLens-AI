import logging
import time
import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ATSParserBase(ABC):
    """
    Base class for generic ATS collectors, enforcing standardization.
    Handles timeout, retry logic, health logging, and telemetry emission.
    """

    def __init__(self, company_name: str, ats_identifier: str, timeout: int = 15, retries: int = 3):
        self.company_name = company_name
        self.ats_identifier = ats_identifier
        self.timeout = timeout
        self.retries = retries

        # Health tracking
        self.health_score = 100
        self.jobs_collected = 0
        self.errors = []

        # Telemetry (Phase 8.7)
        self._run_start: Optional[float] = None
        self._run_end: Optional[float] = None
        self._request_times: List[float] = []
        self._timeout_count: int = 0
        self._retry_successes: int = 0
        self._retry_attempts: int = 0

    @property
    @abstractmethod
    def ats_type(self) -> str:
        """Name of the ATS, e.g. Greenhouse, Lever"""
        pass

    def _make_request(self, url: str, headers: Optional[Dict[str, str]] = None) -> Optional[requests.Response]:
        """Makes an HTTP GET request with retries, timeout, and timing."""
        attempt = 0
        req_start = time.time()

        while attempt < self.retries:
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                elapsed = (time.time() - req_start) * 1000
                self._request_times.append(elapsed)
                if attempt > 0:
                    self._retry_successes += 1
                return response
            except requests.exceptions.Timeout:
                self._timeout_count += 1
                attempt += 1
                self._retry_attempts += 1
                self.health_score -= 10
                self.errors.append(f"Timeout on attempt {attempt}")
                logger.warning(f"[{self.ats_type}] {self.company_name} timed out (Attempt {attempt}/{self.retries})")
            except requests.exceptions.RequestException as e:
                attempt += 1
                self._retry_attempts += 1
                self.health_score -= 10
                self.errors.append(str(e))
                logger.warning(f"[{self.ats_type}] {self.company_name} request failed (Attempt {attempt}/{self.retries}): {e}")

            if attempt >= self.retries:
                self.health_score -= 20
                logger.error(f"[{self.ats_type}] {self.company_name} failed completely.")
                return None

    @abstractmethod
    def fetch_jobs(self) -> Any:
        """Fetches raw data from the ATS API."""
        pass

    @abstractmethod
    def parse_job(self, raw_job: Any) -> Dict[str, Any]:
        """Parses a single raw job into standard format."""
        pass

    def normalize(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Default normalization (cleaning text, basic logic). Can be overridden."""
        if 'title' in job_data and isinstance(job_data['title'], str):
            job_data['title'] = job_data['title'].strip()
        if 'location' in job_data and isinstance(job_data['location'], str):
            job_data['location'] = job_data['location'].strip()

        # Source lineage
        job_data['source'] = self.ats_type
        job_data['company'] = self.company_name
        job_data['collected_at'] = datetime.utcnow()
        job_data['collected_by'] = f"{self.ats_type}_{self.company_name}".lower().replace(" ", "_")
        return job_data

    def health_check(self) -> Dict[str, Any]:
        """Returns health telemetry for this collector run."""
        duration_ms = 0.0
        if self._run_start and self._run_end:
            duration_ms = (self._run_end - self._run_start) * 1000

        avg_req_ms = (
            sum(self._request_times) / len(self._request_times)
            if self._request_times else 0.0
        )
        timeout_rate = (
            self._timeout_count / max(len(self._request_times) + self._timeout_count, 1) * 100
        )
        retry_success_rate = (
            self._retry_successes / max(self._retry_attempts, 1) * 100
        )

        return {
            "collector_name": f"{self.ats_type}_{self.company_name}".lower().replace(" ", "_"),
            "ats_type": self.ats_type,
            "company_name": self.company_name,
            "health_score": max(0, self.health_score),
            "jobs_collected": self.jobs_collected,
            "errors": self.errors,
            "duration_ms": round(duration_ms, 1),
            "avg_response_ms": round(avg_req_ms, 1),
            "timeout_rate": round(timeout_rate, 1),
            "retry_success_rate": round(retry_success_rate, 1),
        }

    def collect(self) -> List[Dict[str, Any]]:
        """Orchestrates fetch -> parse -> normalize with full timing."""
        self._run_start = time.time()
        results = []
        raw_data = self.fetch_jobs()

        if not raw_data:
            self._run_end = time.time()
            return results

        if isinstance(raw_data, list):
            jobs_to_parse = raw_data
        elif isinstance(raw_data, dict) and 'jobs' in raw_data:
            jobs_to_parse = raw_data['jobs']
        else:
            jobs_to_parse = raw_data

        for raw_job in jobs_to_parse:
            try:
                parsed = self.parse_job(raw_job)
                if parsed:
                    normalized = self.normalize(parsed)
                    results.append(normalized)
                    self.jobs_collected += 1
            except Exception as e:
                self.errors.append(f"Parsing error: {e}")
                self.health_score -= 5

        self._run_end = time.time()
        return results

