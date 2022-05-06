from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, \
    HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
import validators
from src.database import User, db
from flasgger import swag_from
from flask import Blueprint, request, render_template, flash, redirect, url_for, send_file, send_from_directory, \
    Response, make_response, session
from flask_login import login_required, current_user
import os
import sqlalchemy
from pprint import pprint
import json

public_1 = Blueprint('public_1', __name__, url_prefix="/api/v1/data/public_1", template_folder='template')


@public_1.route('/', methods=['GET', 'POST'])
@login_required
def handle_public_1():
    if request.method == 'POST':

        queryDetails = request.form
        query_table = queryDetails['table_query']

        if query_table not in ['bank_table']:
            flash('无此表格')
            return redirect(url_for('public_1.handle_public_1'))
        db_engine = db.create_engine(os.environ.get("SQLALCHEMY_DB_URI"), {})
        current_userid = current_user.id
        user = User.query.filter_by(id=current_userid).first()

        current_zuhubh = user.zuhubh
        # page = request.args.get('page', 1, type=int)
        # per_page = request.args.get('per_page', 5, type=int)
        try:
            with db_engine.connect() as conn:
                db_engine.execute("USE basdata")
                # result = db_engine.execute(f"select * from basdata.{query_table} where zuhubh = {current_zuhubh}")
                result_count = db_engine.execute(
                    f"select count(*) from basdata.{query_table} where zuhubh = {current_zuhubh}")
        except sqlalchemy.exc.ProgrammingError as err:
            flash('租户未创建')
            return redirect(url_for('public_1.handle_public_1'))

        # result_ult = jsonify([dict(row) for row in result])
        session['result_count'] = result_count.scalar()

        return redirect(url_for('public_1.query_result',
                                query_table=query_table)), HTTP_200_OK

    return render_template('public.html')


@public_1.route('/results_show/<query_table>/', methods=['GET', 'POST'])
@login_required
def query_result(query_table):
    output = ""
    result_count = session.get('result_count', None)
    output = f"一共查询到{result_count}条数据，请选择下载方式"

    if request.method == 'POST':
        db_engine = db.create_engine(os.environ.get("SQLALCHEMY_DB_URI"), {})
        current_userid = current_user.id
        user = User.query.filter_by(id=current_userid).first()
        current_zuhubh = user.zuhubh
        with db_engine.connect() as conn:
            db_engine.execute("USE basdata")
            result = db_engine.execute(f"select * from basdata.{query_table} where zuhubh = {current_zuhubh}")
        result_ult = jsonify([dict(row) for row in result])

        query_result_form = request.form

        if query_result_form.get('save_excel') == '保存为excel文件':
            response = make_response(result_ult, 200,
                                     {'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'})
            response.headers['Content-Disposition'] = "attachment;filename={}.xlsx".format(query_table)
            return response, HTTP_200_OK
        elif query_result_form.get('save_json') == '保存为json文件':
            # result_ult = pprint(result_ult)
            response = make_response(result_ult, 200, {'mimetype': 'application/json'})
            response.headers['Content-Disposition'] = "attachment;filename={}.json".format(query_table)
            return response, HTTP_200_OK
        elif query_result_form.get('save_csv') == '保存为csv文件':
            response = make_response(result_ult, 200, {'mimetype': 'text/csv'})
            response.headers['Content-Disposition'] = "attachment;filename={}.csv".format(query_table)
            return response, HTTP_200_OK

    # elif request.method == 'GET':
    #     return render_template('results.html')
    return render_template('results.html', form=request.form, output=output)
