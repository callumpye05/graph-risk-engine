using JuMP, GLPK, CSV, DataFrames, Statistics, Redis
#the goal is to minimise the amount of FP's whilst also maximising the amount of fraud caught, by optimally tuning the thresholds of the V2 matrix rules
println(" #### Starting Matrix Optimizer ####")

df = CSV.read("training_data.csv", DataFrame)
N = nrow(df)
M = 1000000.0 

#pre compute to keep things linear
daily_avg =zeros(Float64, N)
pass_through_ratio =zeros(Float64, N)

for i in 1:N
    pure_29d_out =max(0.0, df.total_out_30d[i] -df.total_out_24h[i])
    #enforce a minmum floor
    daily_avg[i]= max(50.0, pure_29d_out /29.0)
    
    #calculate pass through safely 
    if df.total_in_24h[i] >0
        pass_through_ratio[i] = df.total_out_24h[i] / df.total_in_24h[i]
    else
        pass_through_ratio[i] =0.0
    end
end

#linear solver
model =Model(GLPK.Optimizer)

#decision variables
@variable(model, 2.0 <= theta_spike<=15.0)    #sleeper cell spike multiplier
@variable(model,0.70<= theta_pt <= 1.0)       #pass-through threshold, 70% to 100%
@variable(model,flag_spike[1:N], Bin)          #Spike Rule
@variable(model, flag_pt[1:N],Bin)             #pass-through Rule
@variable(model,flagged[1:N], Bin)             #final overall decision

#constraints
for i in 1:N
    #flag_spike can only be 1 if 24h volume  >(daily average *optimal multiplier)
    @constraint(model,df.total_out_24h[i] >= (daily_avg[i] *theta_spike) - M * (1 - flag_spike[i]))
    
    #flag_pt can only be 1 if pass through ratio >=optimal threshold
    # add a volume floor (5000) to match the Python logic so we don't optimize on $10 transactions
    if df.total_out_24h[i] > 5000.0
        @constraint(model, pass_through_ratio[i] >= theta_pt - M * (1 - flag_pt[i]))
    else
        @constraint(model,flag_pt[i]==0)
    end
    
    #Overall flag Logic 
    @constraint(model, flagged[i] <= flag_spike[i] + flag_pt[i])
end

#Objectives
#maximize the number of actual rackets/bots caught
@objective(model, Max, sum(df.is_fraud[i] * flagged[i] for i in 1:N))

#force a strict FP rate (<=1% collateral damage to legitimate retail users)
@constraint(model,sum((1 - df.is_fraud[i]) *flagged[i] for i in 1:N) <= 0.01 * N)

println("Optimizing The Matrix Thresholds...")
optimize!(model)

#export
opt_spike = value(theta_spike)
opt_pt = value(theta_pt)

println("#### Solver Findings ####")
println("Optimal Spike Multiplier: ", round(opt_spike, digits=2), "x")
println("Optimal Pass Through Threshold: ",round(opt_pt, digits=2))

try
    redis_host = get(ENV, "REDIS_HOST", "redis")
    conn = RedisConnection(host=redis_host, port=6379)
    set(conn,"config:std_threshold", string(opt_spike)) 
    set(conn,"config:pass_through_threshold", string(opt_pt))
    
    println("information pushed to Redis successfully")
catch e
    println("redis connection failed: ", e)
end