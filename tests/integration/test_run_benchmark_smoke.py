from benchmarks.run_benchmark import main


def test_main_runs_to_completion_and_writes_output(tmp_path, capsys):
    main(output_dir=tmp_path)

    captured = capsys.readouterr()
    assert "NODE-EXPANSION REDUCTION BENCHMARK" in captured.out

    csv_files = list(tmp_path.glob("*.csv"))
    json_files = list(tmp_path.glob("*.json"))
    assert len(csv_files) == 1
    assert len(json_files) == 1
