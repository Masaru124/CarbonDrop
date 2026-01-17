def calculate_process_emission(processes, total_weight, factors):
    return sum(
        total_weight * factors.get(process, 0)
        for process in processes
    )
