'use client';

import React from 'react';
import { PLButton } from '@/app/components/ui/PL/PLButton/PLButton';

interface RecommendationItem {
  sku: string;
  title: string;
  brand: string;
  category: string;
  style: string;
  abv?: number;
  price?: number;
  score: number;
  reasons: string[];
  qty: number;
  size?: string;
  origin?: string;
  country?: string;
  container?: string;
  varietal?: string;
  wholesale_price?: number;
  retail_price?: number;
  discount_percentage?: number;
  in_stock: boolean;
  region_codes: string[];
  price_volatility?: number;
  trend_direction?: string;
  is_trending: boolean;
}

interface RecommendationsModalProps {
  isOpen: boolean;
  onClose: () => void;
  recommendations: RecommendationItem[];
  query: string;
  confidence: number;
  totalItems: number;
  processingTimeMs: number;
}

// Drink icon component using drinks.svg
const DrinkIcon = ({ category }: { category: string }) => {
  const getIconColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'beer':
        return 'text-amber-600';
      case 'wine':
        return 'text-purple-600';
      case 'spirits':
        return 'text-amber-800';
      case 'cocktail':
        return 'text-pink-600';
      default:
        return 'text-blue-600';
    }
  };

  return (
    <div className={`w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center ${getIconColor(category)}`}>
      <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
        <path fillRule="evenodd" clipRule="evenodd" d="M6.51401 2.6371C6.79387 2.35724 7.17345 2.20001 7.56923 2.20001H9.64615C10.0419 2.20001 10.4215 2.35724 10.7014 2.6371C10.9812 2.91696 11.1385 3.29654 11.1385 3.69232V7.43874C11.7265 7.9023 12.2141 8.48309 12.5692 9.14592C12.9939 9.93867 13.2159 10.8242 13.2154 11.7235V19.6154C13.2154 20.1948 12.9852 20.7505 12.5755 21.1602C12.1658 21.5698 11.6102 21.8 11.0308 21.8H6.18462C5.60522 21.8 5.04955 21.5698 4.63986 21.1602C4.23017 20.7505 4 20.1948 4 19.6154V11.7235C3.99959 10.8243 4.22159 9.93855 4.64621 9.14592C5.0013 8.48309 5.48886 7.9023 6.07692 7.43874V3.69232C6.07692 3.29653 6.23415 2.91696 6.51401 2.6371ZM5.6 18.3384V19.6154C5.6 19.7704 5.66159 19.9191 5.77123 20.0288C5.88087 20.1384 6.02957 20.2 6.18462 20.2H11.0308C11.1858 20.2 11.3345 20.1384 11.4442 20.0288C11.5538 19.9191 11.6154 19.7704 11.6154 19.6154V18.3384H5.6ZM11.6154 16.7384H5.6V13.4924H11.6154V16.7384ZM11.6154 11.7227V11.8924H5.6V11.7227C5.59966 11.0872 5.75651 10.4616 6.05658 9.90147C6.35664 9.34136 6.7906 8.86416 7.31978 8.51241C7.54286 8.36412 7.67692 8.11403 7.67692 7.84617V3.80001H9.53846V7.84617C9.53846 8.11403 9.67252 8.36412 9.89561 8.51241C10.4248 8.86416 10.8587 9.34136 11.1588 9.90147C11.4589 10.4616 11.6157 11.0872 11.6154 11.7227Z" />
        <path fillRule="evenodd" clipRule="evenodd" d="M13.8223 4.61931C14.0707 4.35656 14.4175 4.19994 14.7893 4.19994H16.4257C16.7974 4.19994 17.1443 4.35656 17.3927 4.61931C17.6397 4.88053 17.7711 5.22571 17.7711 5.57686V8.64823C18.2304 9.04202 18.6094 9.52728 18.8867 10.0749C19.2297 10.752 19.4078 11.5057 19.4075 12.2692V18.8461C19.4075 19.3503 19.2185 19.8422 18.8693 20.2116C18.5186 20.5825 18.033 20.7999 17.5166 20.7999H15.6075C15.1657 20.7999 14.8075 20.4418 14.8075 19.9999C14.8075 19.5581 15.1657 19.1999 15.6075 19.1999H17.5166C17.5788 19.1999 17.6482 19.1742 17.7066 19.1124C17.7666 19.049 17.8075 18.954 17.8075 18.8461V17.9153H15.6075C15.1657 17.9153 14.8075 17.5572 14.8075 17.1153C14.8075 16.6735 15.1657 16.3153 15.6075 16.3153H17.8075V13.8769H15.6075C15.1657 13.8769 14.8075 13.5187 14.8075 13.0769C14.8075 12.635 15.1657 12.2769 15.6075 12.2769H17.8075V12.2692C17.8077 11.7538 17.6874 11.248 17.4594 10.7978C17.2315 10.3478 16.9043 9.96939 16.511 9.69284C16.2979 9.54304 16.1711 9.29887 16.1711 9.0384V5.79994H15.0438V7.0384C15.0438 7.48023 14.6857 7.8384 14.2438 7.8384C13.802 7.8384 13.4438 7.48023 13.4438 7.0384V5.57686C13.4438 5.22571 13.5753 4.88053 13.8223 4.61931Z" />
      </svg>
    </div>
  );
};

export default function RecommendationsModal({
  isOpen,
  onClose,
  recommendations,
  query,
  confidence,
  totalItems,
  processingTimeMs
}: RecommendationsModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[9999] overflow-y-auto">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50 transition-opacity" onClick={onClose} />
      
      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden z-10">
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-white relative z-10">
            <div className="flex items-center justify-between">
              <div className="flex-1 pr-4">
                <h2 className="text-2xl font-bold text-gray-900">Drink Recommendations</h2>
                <p className="text-sm text-gray-600 mt-1">
                  Query: &ldquo;{query}&rdquo; • {totalItems} items found • {confidence.toFixed(2)} confidence • {processingTimeMs}ms
                </p>
              </div>
              <button
                onClick={onClose}
                className="flex-shrink-0 text-gray-400 hover:text-gray-600 transition-colors p-2 rounded-full hover:bg-gray-100"
                aria-label="Close modal"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="px-6 py-4 overflow-y-auto max-h-[calc(90vh-120px)]">
            {recommendations.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 mx-auto mb-4 text-gray-400">
                  <svg fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No recommendations found</h3>
                <p className="text-gray-600">Try adjusting your preferences or search criteria.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {recommendations.map((item) => (
                  <div
                    key={item.sku}
                    className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    {/* Product Header */}
                    <div className="flex items-start space-x-3 mb-3">
                      <DrinkIcon category={item.category} />
                      <div className="flex-1 min-w-0">
                        <h3 className="text-sm font-medium text-gray-900 line-clamp-2">
                          {item.title}
                        </h3>
                        <p className="text-xs text-gray-600 mt-1">{item.brand}</p>
                      </div>
                    </div>

                    {/* Product Details */}
                    <div className="space-y-2 text-xs text-gray-600">
                      <div className="flex justify-between">
                        <span>Category:</span>
                        <span className="font-medium">{item.category}</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Style:</span>
                        <span className="font-medium">{item.style}</span>
                      </div>
                      {item.abv && (
                        <div className="flex justify-between">
                          <span>ABV:</span>
                          <span className="font-medium">{item.abv}%</span>
                        </div>
                      )}
                      {item.price && (
                        <div className="flex justify-between">
                          <span>Price:</span>
                          <span className="font-medium text-green-600">${item.price.toFixed(2)}</span>
                        </div>
                      )}
                      <div className="flex justify-between">
                        <span>Score:</span>
                        <span className="font-medium text-blue-600">{(item.score * 100).toFixed(1)}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Qty:</span>
                        <span className="font-medium">{item.qty}</span>
                      </div>
                      {item.size && (
                        <div className="flex justify-between">
                          <span>Size:</span>
                          <span className="font-medium">{item.size}</span>
                        </div>
                      )}
                      {item.origin && (
                        <div className="flex justify-between">
                          <span>Origin:</span>
                          <span className="font-medium">{item.origin}</span>
                        </div>
                      )}
                    </div>

                    {/* Reasons */}
                    {item.reasons && item.reasons.length > 0 && (
                      <div className="mt-3 pt-3 border-t border-gray-100">
                        <p className="text-xs font-medium text-gray-700 mb-1">Why we recommend:</p>
                        <ul className="text-xs text-gray-600 space-y-1">
                          {item.reasons.slice(0, 2).map((reason, index) => (
                            <li key={index} className="flex items-start">
                              <span className="text-green-500 mr-1">•</span>
                              <span>{reason}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Status indicators */}
                    <div className="mt-3 flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {item.in_stock ? (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                            In Stock
                          </span>
                        ) : (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
                            Out of Stock
                          </span>
                        )}
                        {item.is_trending && (
                          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                            Trending
                          </span>
                        )}
                      </div>
                      {item.discount_percentage && item.discount_percentage > 0 && (
                        <span className="text-xs font-medium text-red-600">
                          -{item.discount_percentage}% off
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="px-6 py-4 border-t border-gray-200 bg-gray-50">
            <div className="flex justify-end">
              <PLButton onClick={onClose} hierarchy="primary">
                Close
              </PLButton>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
