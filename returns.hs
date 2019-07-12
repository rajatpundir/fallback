module Returns 
(pricesToPairs
,simpleReturnSinglePeriod
,simpleReturnMultiPeriod
,annualizedReturn
,annualizedReturnApprox
,compoundedAssetValue
,continouslyCompoundedAssetValue
,logReturns
,simplePortfolioReturn
,continouslyCompoundedPortfolioReturnApprox
,simpleReturnOnDividendAsset
,compoundReturnOnDividendAsset
,simpleExcessReturn
,compoundExcessReturn
,simpleToCompoundReturn
,compoundToSimpleReturn
) where

import Data.List

-- Reasons for using asset returns instead of prices :
-- 1. Returns are scale-free.
-- 2. Return series are easier to handle because of their statistical properties.
-- However, there are several definitions of asset returns.

-- Function to convert asset prices to list of pairs.
pricesToPairs :: [Double] -> [(Double, Double)]
pricesToPairs xs = zip xs $ tail xs

-- Simple Return (Single Period)
-- Holding asset for one period.
-- P(t) = P(t-1) + P(t-1) * R(t)
simpleReturnSinglePeriod :: (Double, Double) -> Double
simpleReturnSinglePeriod (p0 , p1) = (p1 - p0) / p0

-- Simple Return (Multiperiod)
-- Holding asset for k periods.
simpleReturnMultiPeriod :: [Double] -> Double
simpleReturnMultiPeriod xs = simpleReturnSinglePeriod (p0, p1)
    where p0 = head xs
          p1 = last xs

-- Annualized(average) return for k years is geometric mean of k opsr.
annualizedReturn :: [Double] -> Double
annualizedReturn xs = exp ((foldl' (\acc (p0, p1)-> acc + log (p1 / p0)) 0 pairs) / k) - 1
    where k = fromIntegral (length xs) :: Double
          pairs = pricesToPairs xs
    
-- If one period returns are small, annualized approximation can be used for speed.
annualizedReturnApprox :: [Double] -> Double
annualizedReturnApprox xs = (foldl' (\acc (p0, p1)-> acc + p1 / p0) 0 pairs) / k
    where k = fromIntegral (length xs) :: Double
          pairs = pricesToPairs xs

-- Compounded Asset Value (over n periods in a year)
-- Here, c is the intial capital, r is the rate per annum to be paid over n periods.
compoundedAssetValue :: Double -> Double -> Double -> Double
compoundedAssetValue c r n = c * (1 + r / n) ** n

-- Continous Compunded Asset Value (over n years)
continouslyCompoundedAssetValue :: Double -> Double -> Double -> Double
continouslyCompoundedAssetValue c r n = c * exp(r * n)

-- Continously Compounded Asset Returns (or Log Returns)
logReturns :: [Double] -> Double
logReturns xs = foldl' (\acc (p0, p1) -> acc + log (p1 / p0)) 0 pairs
    where pairs = pricesToPairs xs

-- Simple Portfolio Return
-- Let p be a portfolio that places w weight on asset i and where r is the simple return for that asset.
-- Simple Portfolio Return is the weighted average of returns for the assets.
simplePortfolioReturn :: [(Double, Double)] -> Double
simplePortfolioReturn xs = foldl' (\acc (w, r) -> acc + w * r) 0 xs

-- Continously Compounded Portfolio Return (Approx.)
continouslyCompoundedPortfolioReturnApprox = simplePortfolioReturn

-- Asset paying Dividends
-- We must separate out dividends on an asset when calculating returns.

-- Simple Return for Asset paying Dividend
simpleReturnOnDividendAsset :: (Double, Double) -> Double -> Double
simpleReturnOnDividendAsset (p0, p1) d = ((p1 - d) / p0) - 1

-- Compound Return for Asset paying Dividend
compoundReturnOnDividendAsset :: (Double, Double) -> Double -> Double
compoundReturnOnDividendAsset (p0, p1) d = log $ simpleReturnOnDividendAsset (p0, p1) d

-- Excess Return
-- Excess Return is defined as asset's return compared to return on some reference asset.

-- Simple Excess Return (Assuming no Dividends are paid by asset)
simpleExcessReturn :: [Double] -> [Double] -> Double
simpleExcessReturn a b = simpleReturnMultiPeriod a - simpleReturnMultiPeriod b

-- Compound Excess Return (Assuming no Dividends are paid by asset)
compoundExcessReturn :: [Double] -> [Double] -> Double
compoundExcessReturn a b = logReturns a - logReturns b

-- Convert Simple Return to Compund Return (Assuming returns are not in percentages)
simpleToCompoundReturn :: Double -> Double
simpleToCompoundReturn r = log(1 + r)

-- Convert Compound Return to Simple Return (Assuming returns are not in percentages)
compoundToSimpleReturn :: Double -> Double
compoundToSimpleReturn r = exp(r) - 1
