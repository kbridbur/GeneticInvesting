from yahoo_finance import Share
import random as rn
import datetime
import numpy

'''
TODO:
  Add complexity to decision algorithm
  Add more features
  Create classes for population and individual
  Increase efficiency
'''

class Chromosome():
  def __init__(self, genes):
    self.genes = genes
    
  def Cross(self, other):
    #DO NOT RETURN AN INSTANCE OF CHROMOSOME, JUST A LIST
  
  
class Single():
  def __init__(self, constant_list, id):
    self.id = id
    chromosomes = [l[i:i+1] for i in range(0, len(constant_list), 2)]
    self.chromosomes = [Chromosome(i) for i in chromosomes]
  
  def Mate(self, other, id):
    child_chromosomes = []
    for chromosome in range(len(self.chromosomes)):
      child_chromosomes.extend(
        self.chromosomes[chromosome].Cross(other.chromosomes[chromosome])
      )
    return Single(child_chromosomes, id)
      
      
class Population()
  def __init__(self, num_individuals, constant_list):
    individuals = []
    for i in range(num_individuals):
      individual_genes = []
      for j in range(3):
        individual_genes.append(rn.random()*(constant_list[1] - constant_list[0])+ constant_list[0])
        individual_genes.append(rn.random()*(constant_list[3] - constant_list[2])+ constant_list[2])
        individual_genes.append(rn.random()*(constant_list[5] - constant_list[4])+ constant_list[4])
      individual_genes.append(rn.random()*(constant_list[7]-constant_list[6])+constant_list[6])
    individuals.append(Single(individual_genes, i))
    self.individuals = individuals

  def Breed(surviving_percent, random_selection_percent, mutation_chance):    

def single(const_min, const_max, quad_min, quad_max, power_min, power_max, buy_amount_min, buy_amount_max):
  coeffs = []
  #randomly generate coefficients within assigned bounds
  for i in range(3):
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
    obv_diff = obv15*10/3 - obv50
    score = get_score(individual, price, sma_slope_diff, obv_diff)
    #buying/selling
    if score > 20000:
      buy_sell_list.append(
        (stock, int((individual[-1]*score)/price))
      )
    if score < 10000:
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
          bought = min(int(gains[i]/price), decision[1])
          stock_counts[i][decision[0]] += bought
          if bought > 0:
              gains[i] -= bought * price         
        if decision[1] < 0:
          sold = min(stock_counts[i][decision[0]], -decision[1])
          stock_counts[i][decision[0]] -= sold
          if sold > 0:
            gains[i] += sold * price
  for i in stock_counts.keys():
    portfolio = stock_counts[i]
    for stock in portfolio.keys():
      price = (float(data[stock][0][u'High'])+float(data[decision[0]][day][u'Low']))/2
      gains[i] += portfolio[stock]*price
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
      pos_to_mutate = rn.randint(0,8)
      if pos_to_mutate <= 6:
        high = max(parent)
        low = min(parent)
      else:
        high = 20
        low = 20
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

def get_score(individual, price, sma_slope_diff, obv_diff):
  #calculate score of individuals constants
  obv_diff /= 1000000
  const_score = individual[0]*price + individual[3]*sma_slope_diff + individual[6]*obv_diff
  quad_score = individual[1]*price**individual[2] + individual[4]*sma_slope_diff**individual[5] + individual[7]*obv_diff**individual[8]
  score = const_score+quad_score
  if type(score) == complex:
    return score.real
  return score
  
#get a good population on a timepoint
scores = []
stocklist = [Share('GOOGL'), Share('TSLA')]
data = get_data(stocklist, "2016-02-01", "2016-08-01")
for trail in range(1):
  population = populate(100, -20, 20, -20, 20, -5, 5, -100, 100)
  for generation in range(100):
    gains = check_success(population, stocklist, data, 30000)
    population = breed(population, gains, .3, .1, .1)
    print(gains[0]/30000)
  print(population[0])
#[83.06244102844536, 81.85830592205076, 65.79228808068581, 80.01920341325118, 83.12176136420138, 83.03874141727889, 10.074165171302429, 20.0, -7.451109241639138, 83.207618791519]
#[66.37426956823778, 79.68530300431567, -1.2548754688505035, 79.72750065680854, -5.783795807268319, -28.66137511260302, 75.03907145852577, 20.0, -1.4341690847473814, 79.9557635317359]

#check a population in a specific time
# population = [ [36.43964415746713, 16.99805550171314, 13.018944963297876, 12.256872408288878, 14.029017840365377, -49.735176925574976, -34.44217469710874, 36.748229452175565, 46.36520887822199, 41.665493443287374, 3.1515366047861164, -12.224114495967168, 6.211164515680534]             ]
# stocklist = [Share('YHOO')]
# data = get_data(stocklist, "2013-03-01", "2016-03-01")
# print(check_success(population, stocklist, data, 3000))
