import unittest
import time
from colorama import Fore


class CustomTextTestResult(unittest.runner.TextTestResult):
    test_run_results = {}
    start_time = 0.0

    def startTestRun(self) -> None:
        self.start_time = time.perf_counter()

    def stopTest(self, test) -> None:
        description = self.getDescription(test)
        status = "PASS" if self.wasSuccessful() else "FAIL"

        self.test_run_results[description] = {
            "errors": self.errors,
            "failures": self.failures,
            "success": self.wasSuccessful(),
            "status": status
        }

        status = Fore.RED + status + \
            Fore.RESET if status == "FAIL" else Fore.GREEN + status + Fore.RESET
        print(description, "...", status)

    def stopTestRun(self) -> None:
        total_time = time.perf_counter() - self.start_time

        failed = [(k, v) for (k, v) in self.test_run_results.items()
                  if v["status"] == "FAIL"]
        total_tests_count = len(self.test_run_results.keys())
        succeded_tests_count = total_tests_count - len(failed)

        for test_name, test in failed:
            print("\n")
            title = f'{Fore.RED + test["status"] + Fore.RESET}: {Fore.YELLOW + test_name + Fore.RESET}'
            print("=" * len(title))
            print(title)
            print("=" * len(title))

            tab = " " * 4

            for type in ["failures", "errors"]:
                items = test[type]

                if len(items) != 0:
                    title = tab + "> " + Fore.RED + type.upper() + Fore.RESET
                    print(title)
                    print(tab + "=" * len("> " + type))

                for messages in items:
                    lines = messages[1].split("\n")
                    lines = "\n".join([f'{tab * 2}{line}' for line in lines])
                    print(lines)

        print("\nSucceded %d of %d tests. Finished test run in %.3fs" %
              (succeded_tests_count, total_tests_count, total_time))
