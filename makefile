

.PHONY: clean random train eval export test dashboard all

clean:
	rm -f my_failures.json ppo_failures.json
	rm -rf models tests/generated
	mkdir -p tests/generated && touch tests/generated/__init__.py


random: clean
	python -m rl_fuzz_bot.tools.random_fuzzer \
	    --episodes 200 --seed 42 --output my_failures.json

train:
	python -m rl_fuzz_bot.tools.train_ppo \
	    --timesteps 10000 --seed 42


eval:
	python -m rl_fuzz_bot.tools.eval_ppo \
	    --model models/ppo_remote_start.zip \
	    --episodes 1000 --seed 42 --output ppo_failures.json

export:
	python -m rl_fuzz_bot.tools.export_tests \
	    --input ppo_failures.json --output tests/generated


test:
	python -m pytest -q


dashboard:
	streamlit run app.py

all: random train eval export test


