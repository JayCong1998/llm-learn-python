from app import ConfigurationError, build_graph


def main() -> int:
    try:
        result = build_graph().invoke(
            {"question": "请用一句话解释 LangGraph 的用途。", "answer": ""}
        )
        print(result["answer"])
    except ConfigurationError as error:
        print(f"Configuration error: {error}")
        return 1
    except Exception as error:
        print(f"Model request failed: {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
