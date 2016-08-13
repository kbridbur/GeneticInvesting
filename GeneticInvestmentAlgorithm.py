from yahoo_finance import Share
import random as rn
import datetime
import numpy

'''
TODO:
  Implement decision algorithm
  Add more features
  Increase efficiency
'''

class Chromosome():
  def __init__(self, genes):
    self.genes = genes
    
  def Cross(self, other):
    #potentially some matrix vector transformation ([1, 2, 3; 4, 5, 6; x, y, z]), add random chance for crossover (ie[1,2,6;4,5,3;x,y,z]) do something and get new chromosome
    a_genes = self.genes
    b_genes = other.genes
    if rn.random() < .3:
      swapped_index = rn.randint(0,2)
      temp = a_genes[swapped_index]
      a_genes[swapped_index] = b_genes[swapped_index]
      b_genes[swapped_index] = temp
      
    a_magnitude = (abs(a_genes[0]**2 + a_genes[1]**2 + a_genes[2]**2))**.5
    b_magnitude = (abs(b_genes[0]**2 + b_genes[1]**2 + b_genes[2]**2))**.5
    resulting_genes = numpy.cross(self.genes, other.genes)
    normalized_genes = [(a_magnitude+b_magnitude)/(2*a_magnitude*b_magnitude)*i for i in resulting_genes]
    return normalized_genes
  
class Single():
  def __init__(self, constant_list):
    chromosomes = [l[i:i+2] for i in range(0, len(constant_list), 3)]
    self.chromosomes = [Chromosome(i) for i in chromosomes]
    self.phenotype = constant_list
  
  def Mate(self, other):
    child_chromosomes = []
    #cross each set of chromosomes
    for chromosome in range(len(self.chromosomes)):
      child_chromosomes.extend(
        self.chromosomes[chromosome].Cross(other.chromosomes[chromosome])
      )
    return Single(child_chromosomes)
      
      
class Population()
  def __init__(self, num_individuals, constant_list):
    self.num_individuals = num_individuals
    individuals = []
    #create a list of Singles with randomly assigned phenotypes
    for i in range(num_individuals):
      individual_genes = []
      #creates chromosomes in order: Constant chromosome, quadratic chromosome, quadratic power chromosome
      for j in range(0, len(constant_list), 2):
        individual_genes.append(rn.random()*(constant_list[j] - constant_list[j+1])+ constant_list[j+1])
        individual_genes.append(rn.random()*(constant_list[j] - constant_list[j+1])+ constant_list[j+1])
        individual_genes.append(rn.random()*(constant_list[j] - constant_list[j+1])+ constant_list[j+1])
    individuals.append(Single(individual_genes, i))
    self.individuals = individuals

  def Rate(stocks_to_test, data, starting_money):
    #Check the performance of a population over a data set
    gains = {}
    stock_counts = {}
    buy_sell_log = {}
    num_days = len(data[stocks_to_test[0]])
    #initialize a dictionary of individuals to their stock portfolios
    for i in range(self.num_individuals):
      buy_sell_log[i] = []
      gains[i] = starting_money
      stock_count = {}
      for stock in stocks_to_test:
        stock_count[stock] = 0
      stock_counts[i] = stock_count
    
    #go through the days and see their behavior
    for day in range(50, num_days):
      features = get_features(stocks_to_test, data, day)
      for i in range(len(population)):
        scores = get_scores(population[i], features)
        buy_sell = evaluate_scores(scores, gains[i], buy_sell_log[i], features)
        for decision in buy_sell:
          price = features[decision[0]][0]
          if decision[1] > 0:
            buy_sell_log[i].append((decision, price, scores[decision[0]))
            gains -= decision[1]*price
          if decision[1] < 0:
            sold = min(stock_counts[i][stock], -decision[1])
            buy_sell_log[i].append(((stock, sold[0]), price, scores[decision[0]))
            gains += sold*price
    #Liquidate all stock remaining at the end of the check period
    for i in stock_counts.keys():
      portfolio = stock_counts[i]
      for stock in portfolio.keys():
        price = (float(data[stock][0][u'High'])+float(data[decision[0]][day][u'Low']))/2
        gains[i] += portfolio[stock]*price
    return gains
    
  def Breed(gains, surviving_percent, random_selection_percent, mutation_chance):  
    graded = [(gains[i], self.individuals[i]) for i in range(self.num_individuals)]
    graded = [x[1] for x in sorted(graded)]
    graded.reverse()
    num_surviving = int(surviving_percent*len(graded))
    parents = graded[:num_surviving]
    possible_variation = graded[num_surviving:]
    
    #take some individuals from the lower performing bunch to increase diversity
    for individual in possible_variation:
      if rn.random() <= random_selection_percent:
        parents.append(individual)
    
    #random mutations for increased diversity
    for parent in parents:
      if rn.random() <= mutation_chance:
        pos_to_mutate = rn.randint(0,8)
        if pos_to_mutate <= 6:
          high = max(parent)
          low = min(parent)
        else:
          high = 20
          low = 20
        parent[pos_to_mutate] = (rn.random()*(high - low)) + low
    
    #fill the remaining slots in the population with "children" of the most fit
    children = []
    wanted_length = self.num_individuals - len(parents)
    while len(children) < wanted_length:
      male = rn.choice(parents)
      female = rn.choice(parents)
      child = male.Mate(female)
      children.append(child)
    parents.extend(children)
    return parents
  
def get_data(stock_list, start_date, end_date):
  #transform date into python form, subtract 50 days, transform back to yahoo_finance form
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
  
  #get a dictionary of stock -> historical data
  data = {}
  for stock in stock_list:
    data[stock] = stock.get_historical(yhoo_start_date, end_date)
  return data
  
def get_features(stocks_to_test, data, current_index):
  #current price, difference between SMA(15) and SMA(50) slopes, SMA(15) concavity, scaled OBV(15) - OBV(50)
  features = {}
  for stock in stocks_to_test:
    #get feature values and how the individual would buy/sell based on them
    sma15, obv15 = get_sma_obv(data[stock], 15, current_index)
    sma50, obv50 = get_sma_obv(data[stock], 50, current_index)
    price =(float(data[stock][current_index][u'High'])+float(data[stock][current_index][u'Low']))/2
    sma15_slope = (sma15[-1] - sma15[0])/len(sma15)
    sma50_slope = (sma50[-1] - sma50[0])/len(sma50)
    sma_slope_diff = sma15_slope - sma50_slope
    obv_diff = (obv15*10/3 - obv50)/1000000
    features[stock] = [price, sma_slope_diff, obv_diff]
  return features

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

def get_scores(individual, features): 
  #calculate score of individuals constants
  scores = {}
  for stock in features.keys():
    const_score = individual.phenotype[0]*features[stock][0] + individual.phenotype[1]*features[stock][1] + individual.phenotype[2]*features[stock][2]
    quad_score = individual.phenotype[3]*features[stock][0]**individual.phenotype[6] + individual.phenotype[4]*features[stock][1]**individual.phenotype[7] + individual.phenotype[5]*features[stock][2]**individual.phenotype[8]
    score = const_score+quad_score
    if type(score) == complex:
      scores[stock] = score.real
    else:
      scores[stock] = score
  return scores

def evaluate_scores(scores, current_money, buy_sell_log, features):
#buy sell log is a list of tuples in the form (stock, amount bought or sold) in chronological order
  money = current_money
  decisions = []
  buy_sell_log.reverse()
  stocks = features.keys()
  percent_allocations = []
  full_score = 0
  for stock in stocks:
    if scores[stock] > 0:
    full_score += scores[stock]
  #Determine splitting of $$ output list of tuples (% of money allocated, stock) as well as selling (append directly to decisions)
  og_split = [(scores[i]/full_score, i) for i in stocks]
#  for stock in stocks:
#    stock_history = []
#    last_stock = None
#    for i in buy_sell_log:
#      if i[0] == stock: stock_history.append(i)   
  
  
  #buy
  for stock in sorted(percent_allocations):
    stock_price = features[stock[0]][0]
    buyable = int(money*stock[1]/stock_price)
    decisions.append(stock[0], buyable)
    money -= stock_price*buyable
  
  #evaluate scores and distribute $$ to each stock niavely. Iter through stocks in reverse order and relalocate left over money proportionally to other stocks
  #something along the lines of compare scores to other times the stock has been bought then see what the gains were from those past times
  
#get a good population on a timepoint
scores = []
stocklist = [Share('GOOGL'), Share('TSLA')]
data = get_data(stocklist, "2016-02-01", "2016-08-01")

#check a population in a specific time
# population = [ [36.43964415746713, 16.99805550171314, 13.018944963297876, 12.256872408288878, 14.029017840365377, -49.735176925574976, -34.44217469710874, 36.748229452175565, 46.36520887822199, 41.665493443287374, 3.1515366047861164, -12.224114495967168, 6.211164515680534]             ]
# stocklist = [Share('YHOO')]
# data = get_data(stocklist, "2013-03-01", "2016-03-01")
# print(check_success(population, stocklist, data, 3000))
