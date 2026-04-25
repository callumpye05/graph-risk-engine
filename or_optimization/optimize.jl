using JuMP, GLPK, CSV, DataFrames, Statistics, Redis

# --- 1. Load the Data ---
df =CSV.read("training_data.csv", DataFrame)
N = nrow(df)
avg_amt =mean(df.amount)
std_amt = std(df.amount)
M =10000 

model = Model(GLPK.Optimizer)

# --- 2. Decision Variables ---
@variable(model, 1.0 <= theta_amt <= 5.0)   # Amount Threshold
@variable(model, 1.0 <= theta_freq <= 10.0) # Max tx per hour
@variable(model, flagged[1:N], Bin)         # Overall Flag

#big m constraints
for i in 1:N
    #flag if amount >(mean + theta_amt *std)
    @constraint(model, df.amount[i] >= (avg_amt +theta_amt *std_amt) - M *(1 - flagged[i]))
    
    #flag if tx_count_1h >theta_freq
    @constraint(model, df.tx_count_1h[i] >= theta_freq - M *(1 - flagged[i]))
end

#maximise true positives 
@objective(model, Max, sum(df.is_fraud[i] * flagged[i] for i in 1:N))

# force a 1% false positive rate 
@constraint(model, sum((1 - df.is_fraud[i]) * flagged[i] for i in 1:N) <= 0.01 * N)

optimize!(model)

#result & redis
opt_amt =value(theta_amt)
opt_freq = value(theta_freq)

println("--- Solver Intel ---")
println("Optimal Amount Threshold: ",opt_amt)
println("Optimal Frequency Limit: ",opt_freq)

try
    redis_host = get(ENV, "REDIS_HOST","redis")
    conn = RedisConnection(host=redis_host, port=6379)
    set(conn, "config:std_threshold",string(opt_amt))
    set(conn, "config:max_tx_per_hour",string(opt_freq))
    println("Intelligence pushed to Redis successfully")
catch e
    println("⚠️ Redis connection failed")
end