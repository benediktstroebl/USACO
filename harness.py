import argparse
from functools import partial
from evaluate import judge_fn_solve
import time
import os
import json


def main(problem_dict_with_responses):
    # if they dont exist create judge_sandbox and code_sandbox
    if not os.path.exists('judge_sandbox'):
        os.makedirs('judge_sandbox/predictions/usaco')
        os.makedirs('judge_sandbox/solutions/usaco')
        
    if not os.path.exists('code_sandbox'):
        os.makedirs('code_sandbox')
        
    # model and judge
    verbose = True
    judge_fn = partial(judge_fn_solve, verbose=verbose)

    if verbose:
        print('Judging...')
        start_time = time.time()
    results = judge_fn(queries=[{"problem_id": problem_id} for problem_id in problem_dict_with_responses], responses=["```python" + problem['response'] + "```" for problem in problem_dict_with_responses.values()], verbose=verbose)
    if verbose:
        print('Finished judging, took {} seconds'.format(time.time() - start_time))

    # nicer result formats
    rdict = {}
    for result in results:
        problem_id = result['problem_id']
        if problem_id not in rdict:
            rdict[problem_id] = []
        rdict[problem_id].append(result)
    rs = list(rdict.values())

    # nicer solution formats
    # note: this sdict / ss includes the result for easier qualitative eval, so may be slightly bulkier
        # no ground truth, e.g. code
    sdict = {}
    for problem_id, problem in problem_dict_with_responses.items():
        solution = problem['response']
        matching_result = None
        for result in results:
            if result['problem_id'] == problem_id:
                matching_result = result
                break

        if problem_id not in sdict:
            sdict[problem_id] = []
        sdict[problem_id].append({
            # 'solution': solution,
            'solution_code': solution,
            'result': matching_result,
            'problem_id': problem_id,
        })
    ss = list(sdict.values())

    return rdict, sdict, rs, ss

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--problem_dict_with_responses', type=str, required=True)
    parser.add_argument("--run_id", type=str, required=True)
    args = parser.parse_args()
    
    # read problem dict with responses
    import json
    with open(args.problem_dict_with_responses, 'r') as f:
        problem_dict_with_responses = json.load(f)

    rdict, sdict, rs, ss = main(problem_dict_with_responses)
    
    # save to results directory
    if not os.path.exists('results'):
        os.makedirs('results')
            
    
    # save rdict, sdict, rs, ss as json files
    with open(f'results/rdict_{args.run_id}.json', 'w') as f:
        json.dump(rdict, f)
    with open(f'results/sdict_{args.run_id}.json', 'w') as f:
        json.dump(sdict, f)
        
    # remove judge_sandbox and code_sandbox
    import shutil
    shutil.rmtree('judge_sandbox')
    shutil.rmtree('code_sandbox')
        
    


