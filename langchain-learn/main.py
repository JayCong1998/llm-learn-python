from app import ConfigurationError, ask_question


def main() -> int:
    try:
        print(ask_question("请用一句话解释 LangChain 的用途。"))
    except ConfigurationError as error:
        print(f"Configuration error: {error}")
        return 1
    except Exception as error:
        print(f"Model request failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
