from typing import Any
import unittest
import time
import unittest.case
from colorama import Fore

class TestFailException(Exception):
    pass

class CustomTextTestResult(unittest.runner.TextTestResult):
    start_time = 0.0
    results = {}

    def addSubTest(self, test: unittest.TestCase, subtest: unittest.TestCase, err: Any | None) -> None:
        super().addSubTest(test, subtest, err)

        test_title = self.getDescription(test)
        subtest_title = self.getDescription(subtest)

        if self.results.get(test_title) is None:
            print(test_title, "...", "RUNNING")

            self.results[test_title] = {
                "subtests": []
            }

        failure = None if len(self.failures) == 0 else self.failures.pop()
        error = None if len(self.errors) == 0 else self.errors.pop()

        if failure is not None:
            status = "FAIL"
            self.results[test_title]["status"] = "FAIL"
        elif error is not None:
            status = "ERROR"
            self.results[test_title]["status"] = "FAIL"
        else:
            status = "PASS"

        print("\t" + subtest_title.replace(test_title + " ", ""),
              "...", self.colorize_status(status))

        self.results[test_title]["subtests"].append({
            "name": subtest_title.replace(test_title + " ", ""),
            "success": err is None,
            "status": status,
            "error": error[1] if error is not None else None,
            "failure": failure[1] if failure is not None else None,
        })

    def addSuccess(self, test: unittest.TestCase) -> None:
        title = self.getDescription(test)
        result = {} if self.results.get(title) is None else self.results[title]

        self.results[title] = {
            **result,
            "success": True,
            "status": "PASS"
        }

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        super().addFailure(test, err)

        title = self.getDescription(test)
        result = {} if self.results.get(title) is None else self.results[title]

        failure = self.failures.pop()

        self.results[title] = {
            **result,
            "failure": failure[1],
            "success": False,
            "status": "FAIL"
        }

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        super().addError(test, err)

        title = self.getDescription(test)
        result = {} if self.results.get(title) is None else self.results[title]

        error = self.errors.pop()

        self.results[title] = {
            **result,
            "error": error[1],
            "success": False,
            "status": "ERROR"
        }

    def startTestRun(self) -> None:
        self.start_time = time.perf_counter()

    def stopTest(self, test) -> None:
        description = self.getDescription(test)

        result = self.results.get(description)

        if result is None:
            return

        if result.get("subtests") is not None:
            return

        status = result["status"]

        status = self.colorize_status(status)
        print(description, "...", status)

    def stopTestRun(self) -> None:
        total_time = time.perf_counter() - self.start_time

        for test_case, reason in self.skipped:
            print("\n")
            title = f'{Fore.LIGHTBLACK_EX + "SKIPPED" + Fore.RESET}: {self.getDescription(test_case)}'
            print("=" * len(title))
            print(" " * len("SKIPPED: ") + Fore.YELLOW + reason + Fore.RESET)
            print(title)
            print("=" * len(title))

        for test_name, result in self.results.items():
            if result.get("status", "PASS") != "PASS":
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

            if result.get("subtests") is not None:
                failed_subtests = [
                    x for x in result["subtests"] if x["status"] != "PASS"]

                for subtest in failed_subtests:
                    tab = " " * 4

                    title = f'{Fore.RED + subtest["status"] + Fore.RESET}: {Fore.YELLOW + subtest["name"] + Fore.RESET}'
                    print(tab + title)
                    print(tab + "=" * len(title))

                    for type in ["failure", "error"]:
                        message = subtest.get(type)
                        if message is None:
                            continue

                        lines = message.split("\n")
                        lines = "\n".join(
                            [f'{tab * 2}{line}' for line in lines])
                        print(lines)

        total_count = 0
        failed_count = 0
        total_subtests_count = 0
        subtests_failed_count = 0
        for result in self.results.values():
            total_count += 1
            if result["status"] != "PASS":
                failed_count += 1
            
            for subtest in result.get("subtests", []):
                total_subtests_count += 1
                if subtest["status"] != "PASS":
                    subtests_failed_count += 1

        succeded_tests_count = total_count - failed_count
        succeded_subtests_count = total_subtests_count - subtests_failed_count
        print("\nSucceded %d of %d tests, %d of %d subtests. Skipped %d. Finished test run in %.3fs\n" %
              (succeded_tests_count, total_count, succeded_subtests_count, total_subtests_count, len(self.skipped), total_time))

        if failed_count != 0:
            raise TestFailException

    def colorize_status(self, status: str):
        if status == "PASS":
            return Fore.GREEN + status + Fore.RESET
        else:
            return Fore.RED + status + Fore.RESET
