from yahoo_finance import Share
import random as rn
import datetime
import numpy

def single(const_min, const_max, quad_min, quad_max, power_min, power_max, exp_min, exp_max, buy_amount_min, buy_amount_max):
  coeffs = []
  #randomly generate coefficients within assigned bounds
  for i in range(3):
    coeffs.append(rn.random()*(const_max - const_min)+ const_min)
    coeffs.append(rn.random()*(quad_max - quad_min)+ quad_min)
    coeffs.append(rn.random()*(power_max - power_min)+ power_min)
    coeffs.append(rn.random()*(exp_max - exp_min)+ exp_min)
  coeffs.append(rn.random()*(buy_amount_max-buy_amount_min)+buy_amount_min)
  return coeffs

def populate(numIndividuals, const_min, const_max, quad_min, quad_max, power_min, power_max, exp_min, exp_max, buy_amount_min, buy_amount_max):
  return [
    single(
      const_min, const_max,
      quad_min, quad_max,
      power_min, power_max,
      exp_min, exp_max,
      buy_amount_min, buy_amount_max
    ) for i in range(numIndividuals)
  ]

#google, tesla, amazon, disney, netflix, twitter
def get_buy_sell(individual, stocks_to_test, current_date):
#current price, difference between SMA(15) and SMA(50) slopes, SMA(15) concavity, OBV(15) - OBV(50)
  buy_sell_list = []
  for stock in stocks_to_test:
    #get feature values and how the individual would buy/sell based on them
    sma15, obv15 = get_sma_obv(stock, 15, current_date)
    sma50, obv50 = get_sma_obv(stock, 50, current_date)
    price = float(stock.get_historical(current_date, current_date)[0][u'High'])
    sma15_slope = (sma15[-1] - sma15[0])/len(sma15)
    sma50_slope = (sma50[-1] - sma50[0])/len(sma50)
    sma_slope_diff = sma15_slope - sma50_slope
    obv_diff = obv15 - obv50
    score = get_score(individual, price, sma_slope_diff, obv_diff)
    #buying/selling
    if score > 100:
      buy_sell_list.append((stock, int((individual[-1]*score)/price)))
    if score < -100:
      buy_sell_list.append((stock, int((individual[-1]*score)/price)))
  return buy_sell_list 

def check_success(population, stocks_to_test, start_date, end_date):
  current_date = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:]))
  yhoo_current_date = start_date
  ending_date = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:]))
  gains = {}
  stock_counts = {}
  #initialize a dictionary of individuals to their stock portfolios
  for i in range(len(population)):
    gains[i] = 0
    stock_count = {}
    for stock in stocks_to_test:
      stock_count[stock] = 0
    stock_counts[i] = stock_count
    
  #go through the days and see their behavior
  while current_date != ending_date:
    if current_date.month >= 10:
      if current_date.day >= 10:
        yhoo_current_date = str(current_date.year) + '-' + str(current_date.month) + '-' + str(current_date.day)
      else: 
        yhoo_current_date = str(current_date.year) + '-' + str(current_date.month) + '-0' + str(current_date.day)
    else:
      if current_date.day >= 10:
        yhoo_current_date = str(current_date.year) + '-0' + str(current_date.month) + '-' + str(current_date.day)
      else: 
        yhoo_current_date = str(current_date.year) + '-0' + str(current_date.month) + '-0' + str(current_date.day)
    if Share('FB').get_historical(yhoo_current_date, yhoo_current_date) != []:
      for i in range(len(population)):
        buy_sell = get_buy_sell(population[i], stocks_to_test, yhoo_current_date)
        for decision in buy_sell:
          stock_counts[i][decision[0]] += decision[1]
          if decision[1] < 0:
            gains[i] += min(-decision[1], stock_counts[i][decision[0]]) * float(decision[0].get_historical(yhoo_current_date, yhoo_current_date)[0][u'High'])
          #if they do not own any of the stock they wish to sell, sell as much as possible and set it to 0
          if stock_counts[i][decision[0]] < 0:
            stock_counts[i][decision[0]] = 0
    current_date += datetime.timedelta(days = 1)
  for i in stock_counts.keys():
    portfolio = stock_counts[i]
    for stock in portfolio.keys():
      if stock.get_historical(yhoo_current_date, yhoo_current_date) != []:
        gains[i] += portfolio[stock]*float(stock.get_historical(yhoo_current_date, yhoo_current_date)[0][u'High'])
  return gains

def breed(population, population_gains, survival_percent, pool_variation_percent, mutation_percent):
  graded = [(population_gains[i], population[i]) for i in range(len(population))]
  print(sorted(graded)[-1][0])
  print(sorted(graded)[0][0])
  graded = [x[1] for x in sorted(graded)]
  graded.reverse()
  num_surviving = int(survival_percent*len(graded))
  parents = graded[:num_surviving]
  possible_variation = [graded[num_surviving:]]
  
  for individual in possible_variation:
    if rn.random() <= pool_variation_percent:
      parents.append(individual)
  
  for parent in parents:
    if rn.random() <= mutation_percent:
      pos_to_mutate = rn.randint(0,16)
      parent[pos_to_mutate] = (rn.random()*(max(parent) - min(parent)))+min(parent)
  
  children = []
  wanted_length = len(population) - len(parents)
  while len(children) < wanted_length:
    male = rn.choice(parents)
    female = rn.choice(parents)
    if male != female:
      child = male[:6] + female[6:]
      children.append(child)
  parents.extend(children)
  return parents
      

def get_sma_obv(stock, size, end_date):
  #convert date to datetime compatible form
  d1 = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:]))
  delta = datetime.timedelta(days = -size)
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
  moving_average = 0
  moving_avg_line = []
  on_balance_volume = 0
  history = stock.get_historical(yhoo_start_date, end_date)
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
  const_score = individual[0]*price + individual[4]*sma_slope_diff + individual[8]*obv_diff
  quad_score = individual[1]*price**individual[2] + individual[5]*sma_slope_diff**individual[6] + individual[9]*obv_diff**individual[10]
  exp_score = price**individual[3] + sma_slope_diff**individual[7] + obv_diff**individual[11]
  score = const_score+quad_score+exp_score
  if type(score) == complex:
    return score.real
  return score
  
  
population = populate(4, -10, 10, -10, 10, -10, 10, -2, 2, 0, 10)
stocklist = [Share('YHOO')]#, Share('GOOGL'), Share('TWTR'), Share('FB')]
for generation in range(50):
  gains = check_success(population, stocklist, "2015-02-15", "2015-03-15")
  population = breed(population, gains, .5, .5, .5)
print(population)
