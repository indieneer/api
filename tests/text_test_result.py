from typing import Any
import unittest
import time
import unittest.case
from colorama import Fore
import sys


class CustomTextTestResult(unittest.runner.TextTestResult):
    start_time = 0.0
    results = {}

    def addSuccess(self, test: unittest.TestCase) -> None:
        self.results[self.getDescription(test)] = {
            "success": True,
            "status": "PASS"
        }

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        super().addFailure(test, err)

        failure = self.failures.pop()

        self.results[self.getDescription(test)] = {
            "failure": failure[1],
            "success": False,
            "status": "FAIL"
        }

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        super().addError(test, err)

        error = self.errors.pop()

        self.results[self.getDescription(test)] = {
            "error": error[1],
            "success": False,
            "status": "ERROR"
        }

    def startTestRun(self) -> None:
        self.start_time = time.perf_counter()

    def stopTest(self, test) -> None:
        description = self.getDescription(test)

        status = self.results[description]["status"]

        status = Fore.GREEN + status + \
            Fore.RESET if status == "PASS" else Fore.RED + status + Fore.RESET
        print(description, "...", status)

    def stopTestRun(self) -> None:
        total_time = time.perf_counter() - self.start_time

        failed = [(k, v) for (k, v) in self.results.items()
                  if v["status"] != "PASS"]
        succeded_tests_count = self.testsRun - len(failed)

        for test_name, test in failed:
            result = self.results[test_name]

            print("\n")
            title = f'{Fore.RED + result["status"] + Fore.RESET}: {Fore.YELLOW + test_name + Fore.RESET}'
            print("=" * len(title))
            print(title)
            print("=" * len(title))

            tab = " " * 4

            for type in ["failure", "error"]:
                message = result.get(type)
                if message is None:
                    continue

                lines = message.split("\n")
                lines = "\n".join([f'{tab}{line}' for line in lines])
                print(lines)

        print("\nSucceded %d of %d tests. Finished test run in %.3fs" %
              (succeded_tests_count, self.testsRun, total_time))

        if len(failed) != 0:
            sys.exit(1)
