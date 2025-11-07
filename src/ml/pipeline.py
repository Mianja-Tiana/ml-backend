import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler

def preprocess_input(df: pd.DataFrame, train_columns: list) -> pd.DataFrame:
    # Feature engineering
    df['TotalCalls'] = df['InboundCalls'] + df['OutboundCalls']
    df.drop(columns=['InboundCalls', 'OutboundCalls'], inplace=True)

    # Handle missing values
    num_features = df.select_dtypes(include=['int64', 'float64']).columns
    cat_features = df.select_dtypes(include=['object', 'category']).columns

    df[num_features] = SimpleImputer(strategy='median').fit_transform(df[num_features])
    df[cat_features] = SimpleImputer(strategy='most_frequent').fit_transform(df[cat_features])

    # binary
    binary_features = ['RespondsToMailOffers', 'MadeCallToRetentionTeam']
    binary_mapping = {'Yes': 1, 'No': 0}
    for col in binary_features:
        if col in df.columns:
            df[col] = df[col].map(binary_mapping).astype(int)

    # one hot encode
    low_card_features = ['CreditRating', 'IncomeGroup', 'Occupation', 'PrizmCode']
    df_onehot = pd.get_dummies(df[low_card_features], drop_first=True)
    df.drop(columns=low_card_features, inplace=True)
    df = pd.concat([df, df_onehot], axis=1)

    # align to training columns
    df = df.reindex(columns=train_columns, fill_value=0)

    # normalize
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = StandardScaler().fit_transform(df[num_cols])

    return df
