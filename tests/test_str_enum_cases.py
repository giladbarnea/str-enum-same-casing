import ast
import enum
from enum import StrEnum, auto, Enum

########################################
# Example cases from README categories #
########################################

# SKIPPED CASES


# Skipped: name and value are different strings
class SkippedDifferentStrings(StrEnum):
    a = "Hello"


# Skipped: only StrEnum subclasses are checked
class SkippedNotStrEnum(Enum):
    a = "a"
    b = "b"


# INVALID CASES


# Invalid: name and value have different case
class InvalidDifferentCase(StrEnum):
    a = "A"


# Invalid: name and value have different case (reverse)
class InvalidDifferentCaseReverse(StrEnum):
    A = "a"


# Invalid: member names have inconsistent case
class InvalidInconsistentNames(StrEnum):
    a = "a"
    B = "B"


# Invalid: member value is auto() and name is uppercase
class InvalidUpperAuto(StrEnum):
    A = auto()


# Invalid: uppercase with qualified auto()
class InvalidUpperQualifiedAuto(StrEnum):
    B = enum.auto()


# Invalid: member names have inconsistent case with auto()
class InvalidMixedWithAuto(StrEnum):
    A = "A"
    b = auto()


# Invalid: complex expressions
ello = "ello"
orld = "orld"


class InvalidComplexValues(StrEnum):
    hello = "H" + ello  # Inconsistent case
    World = f"w{orld}"


# VALID CASES


# Valid: name and value case match (lowercase)
class ValidLowercase(StrEnum):
    a = "a"
    b = "b"


# Valid: name and value case match (uppercase)
class ValidUppercase(StrEnum):
    A = "A"
    B = "B"


# Valid: member value is auto() and name is lowercase
class ValidLowercaseAuto(StrEnum):
    a = auto()
    b = enum.auto()


# Valid: complex expressions
ello = "ello"
arth = "arth"


class ValidComplexValues(StrEnum):
    hello = "h" + ello
    world = enum.auto()
    earth = f"e{arth}"


# ADVANCED TEST CASES


# Test with nested enum
class Outer:
    class NestedEnum(enum.StrEnum):
        a = "A"  # Invalid: mismatched case


# Test case with multiple inheritance
code_multi_inherit = """
from enum import StrEnum

class BaseClass:
    pass

class MultiInherit(BaseClass, StrEnum):
    VALID = "VALID"
    invalid = "INVALID"  # Should be flagged
"""


def test_str_enum_cases():
    """Test all the StrEnum case validation scenarios."""
    import sys
    import os
    import tempfile
    import subprocess
    import contextlib
    from io import StringIO

    # Create a temporary file with our test code
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w+", delete=False
    ) as temp_file:
        with open(__file__, "r") as f:
            temp_file.write(f.read())
        temp_file_path = temp_file.name

    # Get the path to the binary (assuming it's in target/debug)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    binary_path = os.path.join(project_root, "target", "debug", "str_enum_case_check")

    # Run the binary directly
    result = subprocess.run(
        [binary_path, "--path", temp_file_path],
        capture_output=True,
        text=True,
        check=False,
    )

    # Parse the output to get the errors
    errors = [
        line
        for line in result.stdout.splitlines()
        if "StrEnum" in line
        and (
            "inconsistent casing" in line
            or "inconsistent member naming" in line
            or "uppercase member" in line
        )
    ]

    print(f"Found {len(errors)} errors:", errors)

    # Expected invalid classes
    invalid_classes = [
        "InvalidDifferentCase",
        "InvalidDifferentCaseReverse",
        "InvalidInconsistentNames",
        "InvalidUpperAuto",
        "InvalidUpperQualifiedAuto",
        "InvalidMixedWithAuto",
        "InvalidComplexValues",
        "NestedEnum",
    ]

    # Verify all invalid cases are detected
    for class_name in invalid_classes:
        assert any(class_name in error for error in errors), (
            f"Failed to detect invalid class: {class_name}"
        )

    # Verify valid/skipped cases are NOT flagged
    skipped_classes = [
        "SkippedDifferentStrings",
        "SkippedNotStrEnum",
        "ValidLowercase",
        "ValidUppercase",
        "ValidLowercaseAuto",
        "ValidComplexValues",
    ]

    for class_name in skipped_classes:
        assert not any(class_name in error for error in errors), (
            f"Incorrectly flagged valid/skipped class: {class_name}"
        )

    # Create a temporary file for multiple inheritance test
    with tempfile.NamedTemporaryFile(
        suffix=".py", mode="w+", delete=False
    ) as multi_file:
        multi_file.write(code_multi_inherit)
        multi_path = multi_file.name

    # Test multiple inheritance separately
    multi_result = subprocess.run(
        [binary_path, "--path", multi_path], capture_output=True, text=True, check=False
    )

    multi_errors = [
        line
        for line in multi_result.stdout.splitlines()
        if "StrEnum" in line
        and (
            "inconsistent casing" in line
            or "inconsistent member naming" in line
            or "uppercase member" in line
        )
    ]
    assert any("MultiInherit" in error for error in multi_errors), (
        "Failed to detect invalid MultiInherit class"
    )

    # Clean up
    os.unlink(temp_file_path)
    os.unlink(multi_path)

    print("All test cases passed!")


def test_pyproject_toml_config():
    """Test reading configuration from pyproject.toml."""
    import os
    import tempfile
    import subprocess

    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a pyproject.toml file with exclude configuration
        pyproject_content = """
[tool.str-enum-case-check]
exclude = ["excluded_module.py", "excluded_dir"]
"""
        with open(os.path.join(temp_dir, "pyproject.toml"), "w") as f:
            f.write(pyproject_content)

        # Create a module that should be excluded
        excluded_module_content = """
from enum import StrEnum

class ExcludedEnum(StrEnum):
    a = "A"  # This would be an error, but module is excluded
"""
        with open(os.path.join(temp_dir, "excluded_module.py"), "w") as f:
            f.write(excluded_module_content)

        # Create an excluded directory with an invalid file
        excluded_dir = os.path.join(temp_dir, "excluded_dir")
        os.makedirs(excluded_dir, exist_ok=True)
        with open(os.path.join(excluded_dir, "enum_file.py"), "w") as f:
            f.write("""
from enum import StrEnum

class ExcludedDirEnum(StrEnum):
    a = "A"  # This would be an error, but directory is excluded
""")

        # Create a module that should NOT be excluded
        included_module_content = """
from enum import StrEnum

class IncludedEnum(StrEnum):
    a = "A"  # This should be detected as an error
"""
        with open(os.path.join(temp_dir, "included_module.py"), "w") as f:
            f.write(included_module_content)

        # Get the path to the binary (assuming it's in target/debug)
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        binary_path = os.path.join(
            project_root, "target", "debug", "str_enum_case_check"
        )

        # Run the binary on the temp directory
        result = subprocess.run(
            [binary_path, "--path", temp_dir],
            capture_output=True,
            text=True,
            check=False,
        )

        # Parse the output to get the errors
        errors = [line for line in result.stdout.splitlines() if "StrEnum" in line]

        # Check that only the included module was detected
        assert any(
            "IncludedEnum" in error for error in errors
        ), "Failed to detect errors in included module"

        # Check that excluded modules were not detected
        assert not any(
            "ExcludedEnum" in error for error in errors
        ), "Incorrectly checked excluded module"

        assert not any(
            "ExcludedDirEnum" in error for error in errors
        ), "Incorrectly checked file in excluded directory"

        print("Pyproject.toml configuration test passed!")


if __name__ == "__main__":
    test_str_enum_cases()
    test_pyproject_toml_config()
