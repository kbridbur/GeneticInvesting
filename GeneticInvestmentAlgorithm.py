from yahoo_finance import Share
import random as rn
import datetime
import numpy

def single(const_min, const_max, quad_min, quad_max, power_min, power_max, buy_amount_min, buy_amount_max):
  coeffs = []
  #randomly generate coefficients within assigned bounds
  for i in range(2):
    coeffs.append(rn.random()*(const_max - const_min)+ const_min)
    coeffs.append(rn.random()*(quad_max - quad_min)+ quad_min)
    coeffs.append(rn.random()*(power_max - power_min)+ power_min)
  coeffs.append(rn.random()*(buy_amount_max-buy_amount_min)+buy_amount_min)
  return coeffs

def populate(numIndividuals, const_min, const_max, quad_min, quad_max, power_min, power_max, buy_amount_min, buy_amount_max):
  return [
    single(
      const_min, const_max,
      quad_min, quad_max,
      power_min, power_max,
      buy_amount_min, buy_amount_max
    ) for i in range(numIndividuals)
  ]

def get_data(stock_list, start_date, end_date):
  d1 = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:]))
  delta = datetime.timedelta(days = -50)
  start_date = d1 + delta
  if start_date.month >= 10:
    if start_date.day >= 10:
      yhoo_start_date = str(start_date.year) + '-' + str(start_date.month) + '-' + str(start_date.day)
    else: 
      yhoo_start_date = str(start_date.year) + '-' + str(start_date.month) + '-0' + str(start_date.day)
  else:
    if start_date.day >= 10:
      yhoo_start_date = str(start_date.year) + '-0' + str(start_date.month) + '-' + str(start_date.day)
    else: 
      yhoo_start_date = str(start_date.year) + '-0' + str(start_date.month) + '-0' + str(start_date.day)
  
  
  data = {}
  for stock in stock_list:
    data[stock] = stock.get_historical(yhoo_start_date, end_date)
  return data
  
#google, tesla, amazon, disney, netflix, twitter
def get_buy_sell(individual, stocks_to_test, data, current_index):
#current price, difference between SMA(15) and SMA(50) slopes, SMA(15) concavity, OBV(15) - OBV(50)
  buy_sell_list = []
  for stock in stocks_to_test:
    #get feature values and how the individual would buy/sell based on them
    sma15, obv15 = get_sma_obv(data[stock], 15, current_index)
    sma50, obv50 = get_sma_obv(data[stock], 50, current_index)
    price = float(data[stock][current_index][u'High'])
    sma15_slope = (sma15[-1] - sma15[0])/len(sma15)
    sma50_slope = (sma50[-1] - sma50[0])/len(sma50)
    sma_slope_diff = sma15_slope - sma50_slope
    obv_diff = obv15 - obv50
    score = get_score(individual, price, sma_slope_diff, obv_diff)
    #buying/selling
    if score > 100:
      buy_sell_list.append(
        (stock, int((individual[-1]*score)/price))
      )
    if score < -100:
      buy_sell_list.append(
        (stock, int((individual[-1]*score)/price))
      )
  return buy_sell_list 

def check_success(population, stocks_to_test, data, starting_money):
  gains = {}
  stock_counts = {}
  num_days = len(data[stocks_to_test[0]])
  #initialize a dictionary of individuals to their stock portfolios
  for i in range(len(population)):
    gains[i] = starting_money
    stock_count = {}
    for stock in stocks_to_test:
      stock_count[stock] = 0
    stock_counts[i] = stock_count
  
  #go through the days and see their behavior
  for day in range(50, num_days):
    for i in range(len(population)):
      buy_sell = get_buy_sell(population[i], stocks_to_test, data, day)
      for decision in buy_sell:
        price = (float(data[stock][0][u'High'])+float(data[decision[0]][day][u'Low']))/2
        if decision[1] > 0:
          bought = min(gains[i]/price, decision[1])
          stock_counts[i][decision[0]] += bought
          gains[i] -= bought*price
        if decision[1] < 0:
          sold = min(stock_counts[i][decision[0]], -decision[1])
          stock_counts[i][decision[0]] -= sold
          gains[i] += sold*price
  for i in stock_counts.keys():
    portfolio = stock_counts[i]
    for stock in portfolio.keys():
      gains[i] += portfolio[stock]*float(data[stock][0][u'High'])
  print(gains[0])
  return gains

def breed(population, population_gains, survival_percent, pool_variation_percent, mutation_percent):
  graded = [(population_gains[i], population[i]) for i in range(len(population))]
  graded = [x[1] for x in sorted(graded)]
  graded.reverse()
  num_surviving = int(survival_percent*len(graded))
  parents = graded[:num_surviving]
  possible_variation = graded[num_surviving:]
  
  for individual in possible_variation:
    if rn.random() <= pool_variation_percent:
      parents.append(individual)
  
  for parent in parents:
    if rn.random() <= mutation_percent:
      pos_to_mutate = rn.randint(0,10)
      high = max(parent)
      low = min(parent)
      parent[pos_to_mutate] = (rn.random()*(high - low)) + low
  
  children = []
  wanted_length = len(population) - len(parents)
  while len(children) < wanted_length:
    male = rn.choice(parents)
    female = rn.choice(parents)
    child = male[:4] + female[4:]
    children.append(child)
    children.append(child)
  parents.extend(children)
  return parents
      

def get_sma_obv(data, size, current_index):
  #convert date to datetime compatible form
  moving_average = 0
  moving_avg_line = []
  on_balance_volume = 0
  history = data[current_index-size:current_index]
  history.reverse()
  num_days = 0
  prev_day = None
  #calculate obv and sma values
  for day in history:
    num_days += 1
    moving_average += (float(day[u'High']) + float(day[u'Low']))/2
    current_sma = moving_average/num_days
    moving_avg_line.append(current_sma)
    if day != history[0]:
      if float(day[u'High']) > float(prev_day[u'High']):
        on_balance_volume += float(day[u'Volume'])
      if float(day[u'High']) < float(prev_day[u'High']):
        on_balance_volume -= float(day[u'Volume'])
    prev_day = day
  return (moving_avg_line, on_balance_volume)

def get_score(individual, price, sma_slope_diff, not_obv_diff):
  #calculate score of individuals constants
  obv_diff = not_obv_diff/1000000000
  const_score = individual[0]*price + individual[3]*sma_slope_diff + individual[6]*obv_diff
  quad_score = individual[1]*price**individual[2] + individual[4]*sma_slope_diff**individual[5] + individual[7]*obv_diff**individual[8]
  score = const_score+quad_score+exp_score
  if type(score) == complex:
    return score.real
  return score
  
#get a good population on a timepoint  
population = populate(200, -100, 100, -100, 100, -30, 30, -100, 100)
stocklist = [Share('YHOO'), Share('FB')]
data = get_data(stocklist, "2013-08-01", "2016-08-01")
for generation in range(100):
  gains = check_success(population, stocklist, data, 3000)
  population = breed(population, gains, .4, .2, .05)
print(population[0])

#check a population in a specific time
# population = [ [36.43964415746713, 16.99805550171314, 13.018944963297876, 12.256872408288878, 14.029017840365377, -49.735176925574976, -34.44217469710874, 36.748229452175565, 46.36520887822199, 41.665493443287374, 3.1515366047861164, -12.224114495967168, 6.211164515680534]             ]
# stocklist = [Share('YHOO')]
# data = get_data(stocklist, "2013-03-01", "2016-03-01")
# print(check_success(population, stocklist, data, 3000))
